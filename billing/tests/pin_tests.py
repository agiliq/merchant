from django.test import TestCase
from billing import get_gateway, CreditCard
from billing.signals import transaction_was_successful, transaction_was_unsuccessful

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

class PinGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("pin")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2020,
                                      number="4100000000000001",
                                      verification_value="100")

    def testPurchaseSuccess(self):
        self.credit_card.number = '4100000000000001'
        resp = self.merchant.purchase(100.00, self.credit_card, options=OPTIONS)
        self.assertEquals(resp["status"], "FAILURE")

    def testPurchaseFailure(self):
        self.credit_card.number = '4200000000000000'
        resp = self.merchant.purchase(100, self.credit_card, options=OPTIONS)
        self.assertEquals(resp["status"], "SUCCESS")
