from django.test import TestCase
from billing import get_gateway, CreditCard
from billing.signals import *
from billing.models import AuthorizeAIMResponse
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa

class AuthorizeNetAIMGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("authorize_net")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2011, 
                                      number="4222222222222", 
                                      verification_value="100")

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
        resp = self.merchant.purchase(1, self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        # In test mode, the transaction ID from Authorize.net is 0
        self.assertEquals(resp["response"].transaction_id, "0")
        self.assertTrue(isinstance(resp["response"], AuthorizeAIMResponse)) 

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        resp = self.merchant.purchase(1, self.credit_card)
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(6, self.credit_card)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testCreditCardExpired(self):
        resp = self.merchant.purchase(8, self.credit_card)
        self.assertNotEquals(resp["status"], "SUCCESS")
