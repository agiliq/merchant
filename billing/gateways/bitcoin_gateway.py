import bitcoinrpc

from decimal import Decimal

from billing import Gateway, GatewayNotConfigured
from billing.signals import transaction_was_unsuccessful, \
    transaction_was_successful
from billing.utils.credit_card import CreditCard
from django.conf import settings
from django.utils import simplejson as json


class BitcoinGateway(Gateway):
    display_name = "Bitcoin"
    homepage_url = "http://bitcoin.org/"

    def __init__(self):
        test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("bitcoin"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        bitcoin_settings = merchant_settings["bitcoin"]

        self.rpcuser = bitcoin_settings["RPCUSER"]
        self.rpcpassword = bitcoin_settings["RPCPASSWORD"]
        self.host = bitcoin_settings.get("HOST", "127.0.0.1")
        self.port = bitcoin_settings.get("PORT", "8332")
        self.account = bitcoin_settings["ACCOUNT"]
        self.minconf = bitcoin_settings.get("MINCONF", 1)

        self.connection = bitcoinrpc.connect_to_remote(
                self.rpcuser,
                self.rpcpassword,
                self.host,
                self.port
        )

    def get_new_address(self):
        return self.connection.getnewaddress(self.account)

    def get_transactions(self):
        return self.connection.listtransactions(self.account)

    def get_transactions_by_address(self, address):
        all_txns = self.get_transactions()
        return filter(lambda txn: txn.address == address, all_txns)

    def get_txns_sum(self, txns):
        return sum(txn.amount for txn in txns)

    def purchase(self, money, address, options = None):
        options = options or {}
        money = Decimal(str(money))
        txns = self.get_transactions_by_address(address)
        received = self.get_txns_sum(txns)
        response = [txn.__dict__ for txn in txns]
        if received == money:
            transaction_was_successful.send(sender=self,
                                            type="purchase",
                                            response=response)
            return {'status': 'SUCCESS', 'response': response}
        transaction_was_unsuccessful.send(sender=self,
                                          type="purchase",
                                          response=response)
        return {'status': 'FAILURE', 'response': response}
