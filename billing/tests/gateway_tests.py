from django.test import TestCase
from billing.utils.credit_card import CreditCard
from billing import get_gateway

class GatewayTestCase(TestCase):
    def testCorrectClassLoading(self):
        gateway = get_gateway("pay_pal")
        self.assertEquals(gateway.display_name, "PayPal Website Payments Pro")
