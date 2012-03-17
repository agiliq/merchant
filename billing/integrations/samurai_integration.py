from billing import Integration, get_gateway
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.views.decorators.csrf import csrf_exempt
from billing.forms.samurai_forms import SamuraiForm


class SamuraiIntegration(Integration):
    def __init__(self):
        super(SamuraiIntegration, self).__init__()
        self.merchant_key = settings.SAMURAI_MERCHANT_KEY
        self.gateway = get_gateway("samurai")

    def generate_form(self):
        initial_data = self.fields
        form = SamuraiForm(initial=initial_data)
        return form
        
    @csrf_exempt
    def transaction(self, request):
        raise NotImplementedError

    def get_urls(self):
        urlpatterns = patterns('',
           url('^samurai_token/$', self.transaction, name="samurai_transaction")
        )
        return urlpatterns
