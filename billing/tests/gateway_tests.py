from django.test import TestCase
from billing.utils.credit_card import CreditCard
from billing import get_gateway
from billing.gateways.pay_pal_gateway import PaypalGateway

class GatewayTestCase(TestCase):
    def testCorrectClassLoading(self):
        gateway = get_gateway("pay_pal")
        self.assertTrue(isinstance(gateway, PayPalGateway))
