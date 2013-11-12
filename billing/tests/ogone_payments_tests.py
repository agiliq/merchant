from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing import get_integration


@skipIf(not settings.MERCHANT_SETTINGS.get("ogone_payments", None), "gateway not configured")
class OgonePaymentsTestCase(TestCase):
    def setUp(self):
        self.op = get_integration("ogone_payments")
        self.data = {
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
        self.op.add_fields(self.data)

    def testFormFields(self):
        self.assertEquals(self.op.fields, {
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
        })
