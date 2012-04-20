from billing import Integration, get_gateway, IntegrationNotConfigured
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.views.decorators.csrf import csrf_exempt
from billing.forms.samurai_forms import SamuraiForm


class SamuraiIntegration(Integration):
    display_name = "Samurai"

    def __init__(self):
        super(SamuraiIntegration, self).__init__()
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("samurai"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        samurai_settings = merchant_settings["samurai"]
        self.merchant_key = samurai_settings['MERCHANT_KEY']
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
