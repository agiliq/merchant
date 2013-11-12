from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing import get_gateway, CreditCard
from billing.signals import transaction_was_successful, \
    transaction_was_unsuccessful


@skipIf(not settings.MERCHANT_SETTINGS.get("chargebee", None), "gateway not configured")
class ChargebeeGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("chargebee")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2020,
                                      number="4111111111111111",
                                      verification_value="100")

    def testPurchase(self):
        # Purchase is a custom plan created that charges $1000 every 10 years.
        resp = self.merchant.purchase(1, self.credit_card, options = {"plan_id": "purchase"})
        self.assertEquals(resp["status"], "FAILURE")
        resp = self.merchant.purchase(1, self.credit_card,
                                      options = {"plan_id": "purchase",
                                                 "description": "Quick Purchase"})
        self.assertEquals(resp["status"], "SUCCESS")

    def testAuthorizeAndCapture(self):
        resp = self.merchant.authorize(100, self.credit_card,
                                       options = {"plan_id": "purchase",
                                                  "description": "Authorize"})
        self.assertEquals(resp["status"], "SUCCESS")
        response = self.merchant.capture(50, resp["response"]["subscription"]["id"],
                                         options = {"description": "Capture"})
        self.assertEquals(response["status"], "SUCCESS")

    def testAuthorizeAndVoid(self):
        resp = self.merchant.authorize(100, self.credit_card,
                                       options = {"plan_id": "purchase",
                                                  "description": "Authorize"})
        self.assertEquals(resp["status"], "SUCCESS")
        response = self.merchant.void(resp["response"]["subscription"]["id"])
        self.assertEquals(response["status"], "SUCCESS")

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        resp = self.merchant.store(self.credit_card, options={"plan_id": "professional"})
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.store(self.credit_card)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testCreditCardExpired(self):
        credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2011,
                                 number="4000111111111115",
                                 verification_value="100")
        resp = self.merchant.store(credit_card)
        self.assertNotEquals(resp["status"], "SUCCESS")

    def testStoreWithoutCreditCard(self):
        options = {
            "customer[first_name]": "John",
            "customer[last_name]": "Doe",
            "customer[email]": "john.doe@example.com",
            "plan_id": "professional"
            }
        resp = self.merchant.store(None, options=options)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertTrue(resp["response"]["customer"]["object"], "customer")
        self.assertTrue(resp["response"]["customer"]["first_name"], "John")
        self.assertTrue(resp["response"]["customer"]["last_name"], "Doe")
        self.assertTrue(resp["response"]["customer"]["email"], "john.doe@example.com")
        self.assertTrue(resp["response"]["customer"]["card_status"], "no_card")
        self.assertIsNotNone(resp["response"]["customer"]["id"])
        self.assertTrue(resp["response"]["subscription"]["plan_id"], "professional")
        self.assertEquals(resp["response"]["subscription"]["status"], "in_trial")

    def testStoreWithCreditCard(self):
        options = {
            "customer[first_name]": "John",
            "customer[last_name]": "Doe",
            "customer[email]": "john.doe@example.com",
            "plan_id": "professional"
            }
        resp = self.merchant.store(self.credit_card, options=options)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertTrue(resp["response"]["customer"]["object"], "customer")
        self.assertTrue(resp["response"]["customer"]["first_name"], "John")
        self.assertTrue(resp["response"]["customer"]["last_name"], "Doe")
        self.assertTrue(resp["response"]["customer"]["email"], "john.doe@example.com")
        self.assertTrue(resp["response"]["customer"]["card_status"], "valid")
        self.assertIsNotNone(resp["response"]["customer"]["id"])
        self.assertTrue(resp["response"]["subscription"]["plan_id"], "professional")
        self.assertEquals(resp["response"]["subscription"]["status"], "in_trial")

    def testUnstore(self):
        resp = self.merchant.store(self.credit_card, options={"plan_id": "professional"})
        self.assertEquals(resp["status"], "SUCCESS")
        response = self.merchant.unstore(resp["response"]["customer"]["id"])
        self.assertEquals(response["status"], "SUCCESS")
        self.assertEquals(response["response"]["subscription"]["status"], "cancelled")
        response = self.merchant.unstore("abcdef")
        self.assertEquals(response["status"], "FAILURE")
        self.assertEquals(response["response"]["http_status_code"], 404)
        self.assertEquals(response["response"]["error_msg"], "abcdef not found")
