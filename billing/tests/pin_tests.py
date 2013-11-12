from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf
from billing import get_gateway, CreditCard

VISA_SUCCESS = '4200000000000000'
VISA_FAILURE = '4100000000000001'

OPTIONS = {
    "email": "test@test.com",
    "description": "Test transaction",
    "currency": "AUD",
    "ip": "0.0.0.0",
    "billing_address": {
        "address1": "392 Sussex St",
        "address2": "",
        "city": "Sydney",
        "zip": "2000",
        "state": "NSW",
        "country": "Australia",
    },
}


@skipIf(not settings.MERCHANT_SETTINGS.get("pin", None), "gateway not configured")
class PinGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("pin")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2020,
                                      number=VISA_SUCCESS,
                                      verification_value="100")

    def testPurchaseSuccess(self):
        self.credit_card.number = VISA_SUCCESS
        resp = self.merchant.purchase(100, self.credit_card, options=OPTIONS)
        self.assertEquals(resp["status"], "SUCCESS")

    def testPurchaseFailure(self):
        self.credit_card.number = VISA_FAILURE
        resp = self.merchant.purchase(100.00, self.credit_card, options=OPTIONS)
        self.assertEquals(resp["status"], "FAILURE")
