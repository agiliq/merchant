from billing import Integration, get_gateway
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from billing.forms.stripe_forms  import StripeForm


class StripeIntegration(Integration):
    def __init__(self):
        super(StripeIntegration, self).__init__()
        self.gateway = get_gateway("stripe")
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY

    def generate_form(self):
        initial_data = self.fields
        form = StripeForm(initial=initial_data)
        return form

    def transaction(self, request):
        # Subclasses must override this
        raise NotImplementedError

    def get_urls(self):
        urlpatterns = patterns('',
           url('^stripe_token/$', self.transaction, name="stripe_transaction")
        )
        return urlpatterns
