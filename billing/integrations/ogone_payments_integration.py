# -*- coding: utf-8 *-*
from billing import Integration, IntegrationNotConfigured
from django.conf import settings
from django_ogone.ogone import Ogone


class OgonePaymentsIntegration(Integration):
    display_name = "Ogone Payments Integration"

    def __init__(self, options=None):
        if not options:
            options = {}
        super(OgonePaymentsIntegration, self).__init__(options=options)
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("ogone_payments"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        self.ogone_payments_settings = merchant_settings["ogone_payments"]
        self.ogone = Ogone
        self.data = {}

    @property
    def service_url(self):
        return self.ogone.get_action()

    def ogone_notify_handler(self, request):
        pass

    def ogone_success_handler(self, request, response=None):
        pass

    def ogone_failure_handler(self, request, response=None):
        pass

    def get_urls(self):
        pass

    def add_fields(self, params):
        pass

    def generate_tr_data(self):
        data = {
            'orderID': 21,
            'ownerstate': u'',
            'cn': u'Venkata Ramana',
            'language': 'en_US',
            'ownertown': u'Hyderabad',
            'ownercty': u'IN',
            'exceptionurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'ownerzip': u'Postcode',
            'catalogurl': u'http://127.0.0.1:8000/',
            'currency': u'EUR',
            'amount': u'579',
            'declineurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'homeurl': u'http://127.0.0.1:8000/',
            'cancelurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'accepturl': u'http://127.0.0.1:8000/offsite/ogone/success/',
            'owneraddress': u'Near Madapur PS',
            'com': u'Order #21: Venkata Ramana',
            'email': u'ramana@agiliq.com'
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
        form = self.ogone.get_form(self.data, settings=bunch)
        return form
