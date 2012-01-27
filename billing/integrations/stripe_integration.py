from billing import Integration, get_gateway
from django.conf import settings
from django.conf.urls.defaults import patterns, url
import stripe
from billing.forms.stripe_forms  import StripeForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


class StripeIntegration(Integration):
    def __init__(self):
        super(StripeIntegration, self).__init__()
        self.stripe_gateway = get_gateway("stripe")
        stripe.api_key = settings.STRIPE_API_KEY
        self.stripe = stripe

    def generate_form(self):
        initial_data = self.fields
        form = StripeForm(initial=initial_data)
        return form

    @csrf_exempt
    def transaction(self, request):
        # Subclasses must override this
        raise NotImplementedError

    def get_urls(self):
        urlpatterns = patterns('',
           url('^stripe_token/$', self.transaction, name="stripe_transaction"),)
        return urlpatterns
