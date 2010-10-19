from django.test import TestCase
from billing import get_gateway, CreditCard
from billing.signals import *
from paypal.pro.models import PayPalNVP
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa
from paypal.pro.tests import RequestFactory

RF = RequestFactory()
request = RF.get("/", REMOTE_ADDR="192.168.1.1")
fake_options = {
    "request": request,
    "email": "testuser@fakedomain.com",
    "billing_address": {
        "name": "PayPal User",
        "address1": "Street 1",
        "city": "Mountain View",
        "state": "CA",
        "country": "US",
        "zip": "94043"
        },
    # "shipping_address": {
    #     "name": "PayPal User",
    #     "address1": "Street 1",
    #     "city": "Mountain View",
    #     "state": "CA",
    #     "country": "US",
    #     "zip": "94043"
    #     },
}

class PayPalGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("pay_pal")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2011, 
                                      number="4500775008976759", 
                                      verification_value="000")

    def testCardSupported(self):
        self.credit_card.number = "5019222222222222"
        self.assertRaises(CardNotSupported, 
                          lambda : self.merchant.purchase(1000, self.credit_card))

    def testCardValidated(self):
        self.merchant.test_mode = False
        self.credit_card.number = "4222222222222123"
        self.assertFalse(self.merchant.validate_card(self.credit_card))

    def testCardType(self):
        self.merchant.validate_card(self.credit_card)
        self.assertEquals(self.credit_card.card_type, Visa)

    def testPurchase(self):
        resp = self.merchant.purchase(1, self.credit_card, 
                                      options = fake_options)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertNotEquals(resp["response"].correlationid, "0")
        self.assertTrue(isinstance(resp["response"], PayPalNVP)) 

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        resp = self.merchant.purchase(1, self.credit_card,
                                      options = fake_options)
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(105.02, self.credit_card,
                                      options = fake_options)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testCreditCardExpired(self):
        resp = self.merchant.purchase(105.02, self.credit_card,
                                      options = fake_options)
        self.assertNotEquals(resp["status"], "SUCCESS")
