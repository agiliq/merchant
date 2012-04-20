from django.test import TestCase
from billing.utils.credit_card import CreditCard
from billing import get_gateway, GatewayNotConfigured, \
    get_integration, IntegrationNotConfigured
from django.conf import settings
from django.template import Template, Context, TemplateSyntaxError

class MerchantTestCase(TestCase):
    def testCorrectClassLoading(self):
        gateway = get_gateway("authorize_net")
        self.assertEquals(gateway.display_name, "Authorize.Net")

    def testSettingAttributes(self):
        self.assertTrue(getattr(settings, "MERCHANT_SETTINGS", None) != None)
        self.assertTrue(isinstance(settings.MERCHANT_SETTINGS, dict))

    def testRaiseExceptionNotConfigured(self):
        original_settings = settings.MERCHANT_SETTINGS
        settings.MERCHANT_SETTINGS = {
            "google_checkout": {
                "MERCHANT_ID" : '' ,
                "MERCHANT_KEY" : ''
                }
            }

        # Test if we can import any other gateway or integration
        self.assertRaises(IntegrationNotConfigured, lambda: get_integration("stripe"))
        self.assertRaises(GatewayNotConfigured, lambda: get_gateway("authorize_net"))
        settings.MERCHANT_SETTINGS = original_settings

    def testTemplateTagLoad(self):
        original_settings = settings.MERCHANT_SETTINGS
        settings.MERCHANT_SETTINGS = {
            "google_checkout": {
                "MERCHANT_ID" : '' ,
                "MERCHANT_KEY" : ''
                }
            }

        # Raises TemplateSyntaxError: Invalid Block Tag
        self.assertRaises(TemplateSyntaxError, lambda: Template("{% load google_checkout from google_checkout_tags %}{% stripe obj %}"))

        tmpl = Template("{% load google_checkout from google_checkout_tags %}{% google_checkout obj %}")
        gc = get_integration("google_checkout")
        fields = {"items": [{
                    "name": "name of the item",
                    "description": "Item description",
                    "amount": 1,
                    "id": "999AXZ", 
                    "currency": "USD",
                    "quantity": 1,
                    }],
                  "return_url": "http://127.0.0.1:8000/offsite/google-checkout/",
                  }
        gc.add_fields(fields)
        self.assertTrue(len(tmpl.render(Context({"obj": gc}))) > 0)

        settings.MERCHANT_SETTINGS = original_settings
