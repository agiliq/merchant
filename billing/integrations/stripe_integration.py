from billing import Integration, get_gateway, IntegrationNotConfigured
from django.conf import settings
from django.conf.urls import patterns, url
from billing.forms.stripe_forms import StripeForm


class StripeIntegration(Integration):
    display_name = "Stripe"
    template = "billing/stripe.html"

    def __init__(self):
        super(StripeIntegration, self).__init__()
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("stripe"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        stripe_settings = merchant_settings["stripe"]
        self.gateway = get_gateway("stripe")
        self.publishable_key = stripe_settings['PUBLISHABLE_KEY']

    def form_class(self):
        return StripeForm

    def generate_form(self):
        initial_data = self.fields
        form = self.form_class()(initial=initial_data)
        return form

    def transaction(self, request):
        # Subclasses must override this
        raise NotImplementedError

    def get_urls(self):
        urlpatterns = patterns('',
           url('^stripe_token/$', self.transaction, name="stripe_transaction")
        )
        return urlpatterns
