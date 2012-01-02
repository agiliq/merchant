from billing import Integration
from django.conf import settings
from django.conf.urls.defaults import patterns, url
import stripe
from billing.forms.stripe_forms  import StripeForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


class StripeIntegration(Integration):
    def __init__(self):
        super(StripeIntegration, self).__init__()
        stripe.api_key = settings.STRIPE_API_KEY
        self.stripe = stripe

    def generate_form(self):
        initial_data = self.fields
        form = StripeForm(initial=initial_data)
        return form

    @csrf_exempt
    def get_token(self, request):
        token = request.POST['stripeToken']
        return HttpResponse('Success')

    def get_urls(self):
        urlpatterns = patterns('',
           url('^stripe-get-token/$', self.get_token, name="get_token"),)
        return urlpatterns
