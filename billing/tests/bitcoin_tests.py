from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing import get_gateway
from billing.signals import transaction_was_successful, transaction_was_unsuccessful


TEST_AMOUNT = 0.01


@skipIf(not settings.MERCHANT_SETTINGS.get("bitcoin", None), "gateway not configured")
class BitcoinGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("bitcoin")
        self.address = self.merchant.get_new_address()

    def testPurchase(self):
        self.merchant.connection.sendtoaddress(self.address, TEST_AMOUNT)
        resp = self.merchant.purchase(TEST_AMOUNT, self.address)
        self.assertEquals(resp['status'], 'SUCCESS')

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        self.merchant.connection.sendtoaddress(self.address, TEST_AMOUNT)
        self.merchant.purchase(TEST_AMOUNT, self.address)
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        self.merchant.purchase(0.001, self.address)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])
