from billing.integration import Integration, IntegrationNotConfigured
from django.conf import settings
from boto.fps.connection import FPSConnection
from django.conf.urls import patterns, url
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import (HttpResponseForbidden,
                         HttpResponseRedirect,
                         HttpResponse)
from billing.signals import (transaction_was_successful,
                             transaction_was_unsuccessful)
from django.core.urlresolvers import reverse
from billing.models import AmazonFPSResponse
import urlparse
import urllib
import time
import datetime

FPS_PROD_API_ENDPOINT = "fps.amazonaws.com"
FPS_SANDBOX_API_ENDPOINT = "fps.sandbox.amazonaws.com"

csrf_exempt_m = method_decorator(csrf_exempt)
require_POST_m = method_decorator(require_POST)


class AmazonFpsIntegration(Integration):
    """
    Fields required:
    transactionAmount: Amount to be charged/authorized
    paymentReason: Description of the transaction
    paymentPage: Page to direct the user on completion/failure of transaction
    """

    display_name = "Amazon Flexible Payment Service"
    template = "billing/amazon_fps.html"

    def __init__(self, options=None):
        if not options:
            options = {}
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("amazon_fps"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        amazon_fps_settings = merchant_settings["amazon_fps"]
        self.aws_access_key = options.get("aws_access_key", None) or amazon_fps_settings['AWS_ACCESS_KEY']
        self.aws_secret_access_key = options.get("aws_secret_access_key", None) or amazon_fps_settings['AWS_SECRET_ACCESS_KEY']
        super(AmazonFpsIntegration, self).__init__(options=options)
        options.setdefault('host', self.service_url)
        self.fps_connection = FPSConnection(self.aws_access_key, self.aws_secret_access_key, **options)

    @property
    def service_url(self):
        if self.test_mode:
            return FPS_SANDBOX_API_ENDPOINT
        return FPS_PROD_API_ENDPOINT

    @property
    def link_url(self):
        tmp_fields = self.fields.copy()
        tmp_fields.pop("aws_access_key", None)
        tmp_fields.pop("aws_secret_access_key", None)
        tmp_fields.pop("paymentPage", None)
        return self.fps_connection.cbui_url(returnURL=tmp_fields.pop("returnURL"),
                                            paymentReason=tmp_fields.pop("paymentReason"),
                                            pipelineName=tmp_fields.pop("pipelineName"),
                                            transactionAmount=str(tmp_fields.pop("transactionAmount")),
                                            **tmp_fields)

    def purchase(self, amount, options=None):
        if not options:
            options = {}
        tmp_options = options.copy()
        permissible_options = ["SenderTokenId", "CallerReference",
            "SenderDescription", "CallerDescription", "TransactionTimeoutInMins"
            "TransactionAmount", "OverrideIPNURL", "DescriptorPolicy"]
        tmp_options['TransactionAmount'] = amount
        if 'tokenID' in options:
            tmp_options["SenderTokenId"] = options["tokenID"]
        if 'callerReference' in options:
            tmp_options['CallerReference'] = options["callerReference"]
        for key in options:
            if key not in permissible_options:
                tmp_options.pop(key)
        resp = self.fps_connection.pay(**tmp_options)
        return {"status": resp.PayResult.TransactionStatus, "response": resp.PayResult}

    def authorize(self, amount, options=None):
        """ 
        amount: the amount of money to authorize.
        options:
            Required:
                CallerReference
                SenderTokenId
                TransactionAmount

            Conditional:
                SenderDescription

            Optional:
                CallerDescription
                DescriptorPolicy
                OverrideIPNURL
                TransactionTimeoutInMins

            See: http://docs.aws.amazon.com/AmazonFPS/latest/FPSBasicGuide/Reserve.html
            for more info
        """
        if not options:
            options = {}
        options['TransactionAmount'] = amount
        resp = self.fps_connection.reserve(**options)
        return {"status": resp.ReserveResult.TransactionStatus, "response": resp.ReserveResult}

    def capture(self, amount, options=None):
        if not options:
            options = {}
        assert "ReserveTransactionId" in options, "Expecting 'ReserveTransactionId' in options"
        resp = self.fps_connection.settle(options["ReserveTransactionId"], amount)
        return {"status": resp.SettleResult.TransactionStatus, "response": resp.SettleResult}

    def credit(self, amount, options=None):
        if not options:
            options = {}
        assert "CallerReference" in options, "Expecting 'CallerReference' in options"
        assert "TransactionId" in options, "Expecting 'TransactionId' in options"
        resp = self.fps_connection.refund(options["CallerReference"],
                                          options["TransactionId"],
                                          refundAmount=amount,
                                          callerDescription=options.get("description", None))
        return {"status": resp.RefundResult.TransactionStatus, "response": resp.RefundResult}

    def void(self, identification, options=None):
        if not options:
            options = {}
        # Requires the TransactionID to be passed as 'identification'
        resp = self.fps_connection.cancel(identification,
                                          options.get("description", None))
        return {"status": resp.CancelResult.TransactionStatus, "response": resp.CancelResult}

    def get_urls(self):
        urlpatterns = patterns('',
           url(r'^fps-notify-handler/$', self.fps_ipn_handler, name="fps_ipn_handler"),
           url(r'^fps-return-url/$', self.fps_return_url, name="fps_return_url"),
                               )
        return urlpatterns

    @csrf_exempt_m
    @require_POST_m
    def fps_ipn_handler(self, request):
        uri = request.build_absolute_uri()
        parsed_url = urlparse.urlparse(uri)
        resp = self.fps_connection.verify_signature(UrlEndPoint="%s://%s%s" % (parsed_url.scheme,
                                                                  parsed_url.netloc,
                                                                  parsed_url.path),
                                                    HttpParameters=request.raw_post_data)
        if not resp.VerifySignatureResult.VerificationStatus == "Success":
            return HttpResponseForbidden()

        data = dict(map(lambda x: x.split("="), request.raw_post_data.split("&")))
        for (key, val) in data.iteritems():
            data[key] = urllib.unquote_plus(val)
        if AmazonFPSResponse.objects.filter(transactionId=data["transactionId"]).count():
            resp = AmazonFPSResponse.objects.get(transactionId=data["transactionId"])
        else:
            resp = AmazonFPSResponse()
        for (key, val) in data.iteritems():
            attr_exists = hasattr(resp, key)
            if attr_exists and not callable(getattr(resp, key, None)):
                if key == "transactionDate":
                    val = datetime.datetime(*time.localtime(float(val))[:6])
                setattr(resp, key, val)
        resp.save()
        if resp.statusCode == "Success":
            transaction_was_successful.send(sender=self.__class__,
                                            type=data["operation"],
                                            response=resp)
        else:
            if not "Pending" in resp.statusCode:
                transaction_was_unsuccessful.send(sender=self.__class__,
                                                  type=data["operation"],
                                                  response=resp)
        # Return a HttpResponse to prevent django from complaining
        return HttpResponse(resp.statusCode)

    def fps_return_url(self, request):
        uri = request.build_absolute_uri()
        parsed_url = urlparse.urlparse(uri)
        resp = self.fps_connection.verify_signature(UrlEndPoint="%s://%s%s" % (parsed_url.scheme,
                                                                  parsed_url.netloc,
                                                                  parsed_url.path),
                                                    HttpParameters=parsed_url.query)
        if not resp.VerifySignatureResult.VerificationStatus == "Success":
            return HttpResponseForbidden()

        return self.transaction(request)

    def transaction(self, request):
        """Has to be overridden by the subclasses"""
        raise NotImplementedError
