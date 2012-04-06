# -*- coding: utf-8 *-*
from billing import Integration
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

#from django_ogone import settings as ogone_settings
from django.conf import settings
from django_ogone.ogone import Ogone
#from django_ogone import alternative_signing as altsign

class OgonePaymentsIntegration(Integration):
    def __init__(self, options=None):
        if not options:
            options = {}
        super(OgonePaymentsIntegration, self).__init__(options=options)
        self.ogone = Ogone
        self.data = {}

    @property
    def service_url(self):
        return self.ogone.get_action()

    def ogone_notify_handler(self, request):
        pass

    def ogone_success_handler(self, request, response=None):
        return render_to_response("billing/ogone_success.html",
                                  {"response": response},
                                  context_instance=RequestContext(request))

    def ogone_failure_handler(self, request, response=None):
        return render_to_response("billing/ogone_failure.html",
                                  {"response": response},
                                  context_instance=RequestContext(request))

    def get_urls(self):
        pass

    def add_fields(self, params):
        pass

    def generate_tr_data(self):
        data = {
            'orderID': 17,
            'ownerstate': u'',
            'cn': u'Venkata Ramana',
            'language': 'en_US',
            'ownertown': u'Hyderabad',
            'ownercty': u'IN',
            'exceptionurl': u'http://127.0.0.1:8000/failure/',
            'ownerzip': u'Postcode',
            #'catalogurl': u'http://127.0.0.1:8000/',
            'currency': u'EUR',
            'amount': u'579',
            'declineurl': u'http://127.0.0.1:8000/failure/',
            'homeurl': u'http://127.0.0.1:8000/',
            'cancelurl': u'http://127.0.0.1:8000/failure/',
            'accepturl': u'http://127.0.0.1:8000/success/',
            'owneraddress': u'Near Madapur PS',
            'com': u'Order #14: Venkata Ramana',
            'email': u'ramana@agiliq.com'
            }
        data['PSPID'] = settings.PSPID
        return data

    def generate_form(self):
        self.data = self.generate_tr_data()
        form = self.ogone.get_form(self.data, settings=settings)
        return form
