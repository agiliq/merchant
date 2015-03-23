from django.conf import settings
from django.conf.urls import patterns, include

from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
from paypal.standard.models import (ST_PP_ACTIVE, ST_PP_CANCELED_REVERSAL,
                                    ST_PP_COMPLETED, ST_PP_CREATED,
                                    ST_PP_PAID, ST_PP_PENDING,
                                    ST_PP_PROCESSED, ST_PP_REFUNDED,
                                    ST_PP_REWARDED, ST_PP_VOIDED)
from paypal.standard.ipn.signals import valid_ipn_received

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
            raise IntegrationNotConfigured(
                "The '%s' integration is not "
                "correctly configured." % self.display_name)
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


def txn_handler(sender, **kwargs):
    if sender.payment_status in [
            ST_PP_ACTIVE,
            ST_PP_CANCELED_REVERSAL,
            ST_PP_COMPLETED,
            ST_PP_CREATED,
            ST_PP_PAID,
            ST_PP_PENDING,
            ST_PP_PROCESSED,
            ST_PP_REFUNDED,
            ST_PP_REWARDED,
            ST_PP_VOIDED
    ]:
        successful_txn_handler(sender, **kwargs)
    else:
        unsuccessful_txn_handler(sender, **kwargs)

def unsuccessful_txn_handler(sender, **kwargs):
    transaction_was_unsuccessful.send(sender=sender.__class__,
                                      type="purchase",
                                      response=sender)


def successful_txn_handler(sender, **kwargs):
    transaction_was_successful.send(sender=sender.__class__,
                                    type="purchase",
                                    response=sender)

valid_ipn_received.connect(txn_handler)
