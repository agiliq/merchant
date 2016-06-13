import mock
import decimal

from bitcoinrpc.data import TransactionInfo

from django.conf import settings
from django.test import TestCase
from django.utils.unittest import skipIf

from billing import get_gateway
from billing.signals import transaction_was_successful, transaction_was_unsuccessful


TEST_AMOUNT = decimal.Decimal('0.01')
TEST_ADDRESS = 'n2RL9NRRGvKNqovb14qacSfbz6zQBkzDbU'
TEST_SUCCESSFUL_TXNS = [TransactionInfo(address=TEST_ADDRESS, amount=TEST_AMOUNT)]


@skipIf(not settings.MERCHANT_SETTINGS.get("bitcoin", None), "gateway not configured")
class BitcoinGatewayTestCase(TestCase):

    def setUp(self):
        with mock.patch('bitcoinrpc.connection.BitcoinConnection') as MockBitcoinConnection:
            connection = MockBitcoinConnection()
            connection.getnewaddress.return_value = TEST_ADDRESS
            connection.listtransactions.return_value = TEST_SUCCESSFUL_TXNS
            self.merchant = get_gateway("bitcoin")
            self.address = self.merchant.get_new_address()

    def testPurchase(self):
            resp = self.merchant.purchase(TEST_AMOUNT, self.address)
            self.assertEquals(resp['status'], 'SUCCESS')

    def testPaymentSuccessfulSignal(self):
            received_signals = []

            def receive(sender, **kwargs):
                received_signals.append(kwargs.get("signal"))

            transaction_was_successful.connect(receive)

            self.merchant.purchase(TEST_AMOUNT, self.address)
            self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
            received_signals = []

            def receive(sender, **kwargs):
                received_signals.append(kwargs.get("signal"))

            transaction_was_unsuccessful.connect(receive)

            self.merchant.purchase(TEST_AMOUNT/2, self.address)
            self.assertEquals(received_signals, [transaction_was_unsuccessful])
