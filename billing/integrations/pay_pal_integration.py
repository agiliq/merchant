from billing import Integration, IntegrationNotConfigured
from django.conf import settings
from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
from django.conf.urls.defaults import patterns, include
from paypal.standard.ipn.signals import payment_was_flagged, payment_was_successful
from billing.signals import transaction_was_successful, transaction_was_unsuccessful

class PayPalIntegration(Integration):
    display_name = "PayPal IPN"

    def __init__(self):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("pay_pal"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        pay_pal_settings = merchant_settings["pay_pal"]
        # Required Fields. Just a template for the user
        self.fields = {"business": pay_pal_settings['RECEIVER_EMAIL'],
                       "item_name": "",
                       "invoice": "",
                       "notify_url": "",
                       "return_url": "",
                       "cancel_return": "",
                       "amount": 0,
                       }

    @property
    def service_url(self):
        if self.test_mode:
            return SANDBOX_POSTBACK_ENDPOINT
        return POSTBACK_ENDPOINT

    def get_urls(self):
        urlpatterns = patterns('',
           (r'^', include('paypal.standard.ipn.urls')),
            )
        return urlpatterns

def unsuccessful_txn_handler(sender, **kwargs):
    transaction_was_unsuccessful.send(sender=sender.__class__,
                                      type="purchase",
                                      response=sender)

def successful_txn_handler(sender, **kwargs):
    transaction_was_successful.send(sender=sender.__class__,
                                    type="purchase",
                                    response=sender)

payment_was_flagged.connect(unsuccessful_txn_handler)
payment_was_successful.connect(successful_txn_handler)
