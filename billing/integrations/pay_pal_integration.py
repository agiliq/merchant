from django.conf import settings
from django.conf.urls import patterns, include

from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
from paypal.standard.ipn.signals import (payment_was_flagged,
                                         payment_was_successful)

from billing import Integration, IntegrationNotConfigured
from billing.forms.paypal_forms import (MerchantPayPalPaymentsForm,
                                        MerchantPayPalEncryptedPaymentsForm)
from billing.signals import (transaction_was_successful,
                             transaction_was_unsuccessful)


class PayPalIntegration(Integration):
    display_name = "PayPal IPN"
    template = "billing/paypal.html"

    def __init__(self):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("pay_pal"):
            raise IntegrationNotConfigured("The '%s' integration is not \
                                    correctly configured." % self.display_name)
        pay_pal_settings = merchant_settings["pay_pal"]
        self.encrypted = False
        if pay_pal_settings.get("ENCRYPTED"):
            self.encrypted = True
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
        urlpatterns = patterns('', (r'^', include('paypal.standard.ipn.urls')))
        return urlpatterns

    def form_class(self):
        if self.encrypted:
            return MerchantPayPalEncryptedPaymentsForm
        return MerchantPayPalPaymentsForm

    def generate_form(self):
        return self.form_class()(initial=self.fields)


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
