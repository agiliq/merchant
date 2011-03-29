from billing.integration import Integration
from django.conf import settings
from boto.fps.connection import FPSConnection
from django.conf.urls.defaults import patterns, url
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import (HttpResponseForbidden, 
                         HttpResponseRedirect, 
                         HttpResponse)
from billing.signals import (amazon_fps_payment_signal, 
                             transaction_was_successful,
                             transaction_was_unsuccessful)
from django.core.urlresolvers import reverse
from billing.models import AmazonFPSResponse
import urlparse

FPS_PROD_API_ENDPOINT = "fps.amazonaws.com"
FPS_SANDBOX_API_ENDPOINT = "fps.sandbox.amazonaws.com"

csrf_exempt_m = method_decorator(csrf_exempt)
require_POST_m = method_decorator(require_POST)

class AmazonFpsIntegration(Integration):
    fields = {"transactionAmount": "",
              "pipelineName": "",
              "paymentReason": "",
              # Page on the merchant site from
              # where the user got redirected to FPS
              # Used to get him back after the transaction
              # is completed
              "paymentPage": "",
              # Slight modification of FPS attr
              "returnURLPrefix": "",
              }

    def __init__(self, options={}):
        self.aws_access_key = options.get("aws_access_key", None) or settings.AWS_ACCESS_KEY
        self.aws_secret_access_key = options.get("aws_secret_access_key", None) or settings.AWS_SECRET_ACCESS_KEY
        super(AmazonFpsIntegration, self).__init__(options=options)
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
        tmp_fields.pop("returnURL", None)
        tmp_fields.pop("paymentPage", None)
        return self.fps_connection.make_url("%s%s" %(tmp_fields.pop("returnURLPrefix"), 
                                                     reverse("fps_return_url")),
                                            tmp_fields.pop("paymentReason"),
                                            tmp_fields.pop("pipelineName"),
                                            str(tmp_fields.pop("transactionAmount")),
                                            **tmp_fields)

    def purchase(self, amount, options={}):
        tmp_options = options.copy()
        permissible_options = ["senderTokenId", "recipientTokenId", 
            "chargeFeeTo", "callerReference", "senderReference", "recipientReference",
            "senderDescription", "recipientDescription", "callerDescription",
            "metadata", "transactionDate", "reserve"]
        tmp_options["senderTokenId"] = options["tokenID"]
        for key in options:
            if key not in permissible_options:
                tmp_options.pop(key)
        resp = self.fps_connection.pay(amount, tmp_options.pop("senderTokenId"), 
                                       callerReference=tmp_options.pop("callerReference"),
                                       **tmp_options)
        return {"status": resp[0].TransactionStatus, "response": resp[0]}

    def authorize(self, amount, options={}):
        options["reserve"] = True
        return self.purchase(amount, options)

    def capture(self, amount, options={}):
        assert "ReserveTransactionId" in options, "Expecting 'ReserveTransactionId' in options"
        resp = self.fps_connection.settle(options["ReserveTransactionId"], amount)
        return {"status": resp[0].TransactionStatus, "response": resp[0]}

    def credit(self, amount, options={}):
        assert "CallerReference" in options, "Expecting 'CallerReference' in options"
        assert "TransactionId" in options, "Expecting 'TransactionId' in options"
        resp = self.fps_connection.refund(options["CallerReference"],
                                          options["TransactionId"], 
                                          refundAmount=amount,
                                          callerDescription=options.get("description", None))
        return {"status": resp[0].TransactionStatus, "response": resp[0]}

    def void(self, identification, options={}):
        # Requires the TransactionID to be passed as 'identification'
        resp = self.fps_connection.cancel(identification, 
                                          options.get("description", None))
        return {"status": resp[0].TransactionStatus, "response": resp[0]}

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
        resp = self.fps_connection.verify_signature("%s://%s%s" %(parsed_url.scheme, 
                                                                  parsed_url.netloc, 
                                                                  parsed_url.path),
                                                    parsed_url.query)
        if not resp[0].VerificationStatus == "Success":
            return HttpResponseForbidden()

        data = request.POST.copy()
        if AmazonFPSResponse.objects.filter(transactionId=data["transactionId"]).count():
            resp = AmazonFPSResponse.objects.get(transactionId=data["transactionId"])
        else:
            resp = AmazonFPSResponse()
        for (key, val) in data.iteritems():
            model_inst_attr = getattr(resp, key, None)
            if model_inst_attr and not callable(model_inst_attr):
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
        resp = self.fps_connection.verify_signature("%s://%s%s" %(parsed_url.scheme, 
                                                                  parsed_url.netloc, 
                                                                  parsed_url.path),
                                                    parsed_url.query)
        if not resp[0].VerificationStatus == "Success":
            return HttpResponseForbidden()
        
        amazon_fps_payment_signal.send(sender=self.__class__, 
                                       request=request, 
                                       integration=self)
        return HttpResponseRedirect(self.fields["paymentPage"])
