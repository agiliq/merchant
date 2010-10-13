from django.test import TestCase
from django.conf import settings
from billing import get_gateway
from billing.signals import *
from billing.models.authorize_models import AuthorizeAIMResponse
from billing.utils.credit_card import CreditCard

class AuthorizeNetAIMGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("authorize_net")
        self.credit_card = CreditCard(first_name="Test", last_name="User", 
                                      month=10, year=2011, 
                                      number="4222222222222222", 
                                      card_type="visa", 
                                      verification_value="100")

    def testPurchase(self):
        resp = self.merchant.purchase(1, self.credit_card)
        self.assertEquals(resp.status, "SUCCESS")
        # In test mode, the transaction ID from Authorize.net is 0
        self.assertEquals(resp.transaction_id, "0")
        self.assertTrue(isinstance(resp.actual, AuthorizeAIMResponse)) 

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def recieve(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        payment_was_succesful.connect(recieve)

        resp = self.merchant.purchase(1000, self.credit_card)
        self.assertEquals(recieved_signals, [payment_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def recieve(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        payment_was_unsuccesful.connect(recieve)

        resp = self.merchant.purchase(6, self.credit_card)
        self.assertEquals(recieved_signals, [payment_was_unsuccessful])

    def testCreditCardExpired(self):
        resp = self.merchant.purchase(8, self.credit_card)
        self.assertNotEquals(resp.status, "SUCCESS")

