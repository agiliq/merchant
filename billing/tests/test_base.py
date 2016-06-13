from django.conf import settings
from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError
from django.utils.unittest import skipIf

from billing.utils.credit_card import CreditCard
from billing import get_gateway, GatewayNotConfigured, get_integration, IntegrationNotConfigured


class MerchantTestCase(TestCase):

    @skipIf(not settings.MERCHANT_SETTINGS.get("authorize_net", None), "gateway not configured")
    def testCorrectClassLoading(self):
        gateway = get_gateway("authorize_net")
        self.assertEquals(gateway.display_name, "Authorize.Net")

    def testSettingAttributes(self):
        self.assertTrue(getattr(settings, "MERCHANT_SETTINGS", None) != None)
        self.assertTrue(isinstance(settings.MERCHANT_SETTINGS, dict))

    def testRaiseExceptionNotConfigured(self):
        with self.settings(MERCHANT_SETTINGS = {
                "pay_pal": {
                }
        }):
            # Test if we can import any other gateway or integration
            self.assertRaises(IntegrationNotConfigured, lambda: get_integration("stripe"))
            self.assertRaises(GatewayNotConfigured, lambda: get_gateway("authorize_net"))

    def testTemplateTagLoad(self):
        with self.settings(MERCHANT_SETTINGS = {
                "pay_pal": {
                }
        }):
            # Raises TemplateSyntaxError: Invalid Block Tag
            self.assertRaises(TemplateSyntaxError, lambda: Template("{% load render_integration from billing_tags %}{% stripe obj %}"))

        tmpl = Template("{% load render_integration from billing_tags %}{% render_integration obj %}")
        gc = get_integration("stripe")
        self.assertTrue(len(tmpl.render(Context({"obj": gc}))) > 0)


class CreditCardTestCase(TestCase):
    def test_constructor(self):
        opts = dict(number='x', year=2000, month=1, verification_value='123')
        self.assertRaises(TypeError, lambda: CreditCard(**opts))
        self.assertRaises(TypeError, lambda: CreditCard(first_name='x', **opts))
        self.assertRaises(TypeError, lambda: CreditCard(last_name='y', **opts))
        c = CreditCard(first_name='x', last_name='y', **opts)
        self.assertEqual(c.cardholders_name, None)
        c2 = CreditCard(cardholders_name='z', **opts)
        self.assertEqual(c2.cardholders_name, 'z')
