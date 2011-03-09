from billing import Integration
from django.conf import settings
from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
from django.conf.urls.defaults import patterns, include

class PayPalIntegration(Integration):
    # Required Fields. Just a template for the user
    fields = {"business": settings.PAYPAL_RECEIVER_EMAIL,
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
