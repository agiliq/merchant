from django.test import TestCase
from billing import get_gateway
from billing.signals import *
from billing.models import EwayResponse
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa


class BitcoinGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("bitcoin")
        self.address = self.merchant.get_new_address()

    def testPurchase(self):
        self.merchant.connection.sendtoaddress(self.address, 1)
        resp = self.merchant.purchase(1, self.address)
        self.assertEquals(resp['status'], 'SUCCESS')

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        self.merchant.connection.sendtoaddress(self.address, 1)
        resp = self.merchant.purchase(1, self.address)
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(0.01, self.address)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])
