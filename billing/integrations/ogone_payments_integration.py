# -*- coding: utf-8 *-*
from billing import Integration, IntegrationNotConfigured
from django.conf import settings
from django_ogone.ogone import Ogone
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf.urls import patterns, url
from django_ogone.status_codes import get_status_category, get_status_description
from django_ogone.signals import ogone_payment_accepted, ogone_payment_failed, ogone_payment_cancelled


class OgonePaymentsIntegration(Integration):
    display_name = "Ogone Payments Integration"
    template = "billing/ogone_payments.html"

    def __init__(self, options=None):
        if not options:
            options = {}
        super(OgonePaymentsIntegration, self).__init__(options=options)
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("ogone_payments"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        self.ogone_payments_settings = merchant_settings["ogone_payments"]
        self.data = {}

    @property
    def service_url(self):
        return Ogone.get_action()

    # orderID=26&currency=INR&amount=5%2E79&PM=CreditCard&ACCEPTANCE=test123&STATUS=5&CARDNO=XXXXXXXXXXXX1111&ED=0314&CN=Ramana+C&TRXDATE=05%2F15%2F13&PAYID=21604838&NCERROR=0&BRAND=VISA&IP=202%2E65%2E155%2E202&SHASIGN=FF9B8F20CAA6F9E8BA803C560BCF24111EF557A3118DFCD6CFBFE08CAA5BD6EB738803466D81C93E10DF8DEE07F0F6B46996BF7E99596B4920272D89DC9E933B
    def ogone_notify_handler(self, request):
        fpath = request.get_full_path()
        query_string = fpath.split("?", 1)[1]
        transaction_feedback = query_string.split('&')
        result = {}
        for item in transaction_feedback:
            k, v = item.split("=")
            result[k] = v

        # Default transaction feedback parameters
        status = result.get('status', False)
        orderid = result.get('orderID', '')
        payid = result.get('PAYID', '')
        ncerror = result.get('NCERROR', '')

        amount = result.get('amount', '')
        currency = result.get('currency', '')

        if status and get_status_category(int(status)) == 'success':
            ogone_payment_accepted.send(sender=self, order_id=orderid, \
                amount=amount, currency=currency, pay_id=payid, status=status, ncerror=ncerror)
            return self.ogone_success_handler(request, response=result, description=get_status_description(status))

        if status and get_status_category(int(status)) == 'cancel':
            ogone_payment_cancelled.send(sender=self, order_id=orderid, \
                amount=amount, currency=currency, pay_id=payid, status=status, ncerror=ncerror)
            return self.ogone_cancel_handler(request, response=result, description=get_status_description(status))

        if status and get_status_category(int(status)) == 'decline' or 'exception':
            ogone_payment_failed.send(sender=self, order_id=orderid, \
                amount=amount, currency=currency, pay_id=payid, status=status, ncerror=ncerror)
            return self.ogone_failure_handler(request, response=result, description=get_status_description(status))

    def ogone_success_handler(self, request, response=None, description=''):
        return render_to_response("billing/ogone_success.html",
                                  {"response": response, "message": description},
                                  context_instance=RequestContext(request))

    def ogone_failure_handler(self, request, response=None, description=''):
        return render_to_response("billing/ogone_failure.html",
                                  {"response": response, "message": description},
                                  context_instance=RequestContext(request))

    def ogone_cancel_handler(self, request, response=None, description=''):
        return render_to_response("billing/ogone_cancel.html",
                                  {"response": response, "message": description},
                                  context_instance=RequestContext(request))

    def get_urls(self):
        urlpatterns = patterns('',
           url('^ogone_notify_handler/$', self.ogone_notify_handler, name="ogone_notify_handler"),)
        return urlpatterns

    def add_fields(self, params):
        pass

    def generate_tr_data(self):
        data = {
            'orderID': 30,
            'currency': u'INR',
            'amount': u'100',
            'language': 'en_US',
            # Optional:
            'exceptionurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'declineurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'cancelurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'accepturl': u'http://127.0.0.1:8000/offsite/ogone/success/',
            # 'homeurl': u'http://127.0.0.1:8000/',
            # 'catalogurl': u'http://127.0.0.1:8000/',
            # 'ownerstate': u'',
            # 'cn': u'Venkata Ramana',
            # 'ownertown': u'Hyderabad',
            # 'ownercty': u'IN',
            # 'ownerzip': u'Postcode',
            # 'owneraddress': u'Near Madapur PS',
            # 'com': u'Order #21: Venkata Ramana',
            # 'email': u'ramana@agiliq.com'
        }
        return data

    def generate_form(self):
        class Bunch(dict):
            def __init__(self, **kw):
                dict.__init__(self, kw)
                self.__dict__ = self
        self.data = self.generate_tr_data()
        bunch = Bunch()
        bunch.update(self.ogone_payments_settings)
        form = Ogone.get_form(self.data, settings=bunch)
        return form
