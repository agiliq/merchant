from django.test import TestCase
from billing.utils.credit_card import CreditCard
from billing import get_gateway, get_integration, NotConfiguredError
from django.conf import settings
from billing.templatetags.billing_tags import register
import inspect
from django.template import Template

class MerchantTestCase(TestCase):
    def testCorrectClassLoading(self):
        gateway = get_gateway("pay_pal")
        self.assertEquals(gateway.display_name, "PayPal Website Payments Pro")

    def testSettingAttributes(self):
        self.assertTrue(getattr(settings, "MERCHANT_SETTINGS", None) != None)
        self.assertTrue(isinstance(settings.MERCHANT_SETTINGS, dict))

    def testRaiseExceptionNotConfigured(self):
        original_settings = settings.MERCHANT_SETTINGS
        settings.MERCHANT_SETTINGS = {
            "google_checkout": {
                "GOOGLE_CHECKOUT_MERCHANT_ID" : '' ,
                "GOOGLE_CHECKOUT_MERCHANT_KEY" : ''
                }
            }

        # Test if we can import any other integration
        self.assertRaises(get_integration("pay_pal"), NotConfiguredError)
        settings.MERCHANT_SETTINGS = original_settings

    def testTemplateTagLoad(self):
        original_settings = settings.MERCHANT_SETTINGS
        settings.MERCHANT_SETTINGS = {
            "google_checkout": {
                "GOOGLE_CHECKOUT_MERCHANT_ID" : '' ,
                "GOOGLE_CHECKOUT_MERCHANT_KEY" : ''
                }
            }
        self.assertEqual(len(register.tags), 1)
        self.assertTrue(inspect.isfunction(register.tags['google_checkout']))
        self.assertTrue(register.tags.get('pay_pal', None) == None)

        self.assertRaises(Template("{% load billing_tags %}{% pay_pal obj %}"),
                          NotConfiguredError)

        settings.MERCHANT_SETTINGS = original_settings
