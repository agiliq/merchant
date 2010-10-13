from django.test import TestCase
from billing.utils.credit_card import CreditCard
from billing import get_gateway
from billing.gateways.paypal_gateway import PaypalGateway

class GatewayTestCase(TestCase):
    def testCorrectClassLoading(self):
        gateway = get_gateway("paypal")
        self.assertTrue(isinstance(gateway, PaypalGateway))
