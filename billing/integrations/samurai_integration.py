from billing import Integration
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from billing.forms.samurai_forms import SamuraiForm


class SamuraiIntegration(Integration):
    def __init__(self):
        super(SamuraiIntegration, self).__init__()

    def generate_form(self):
        initial_data = self.fields
        form = SamuraiForm(initial=initial_data)
        return form

        
    @csrf_exempt
    def get_token(self, request):
        token = request.POST['samuraiToken']
        return HttpResponse('Success')

    def get_urls(self):
        urlpatterns = patterns('',
           url('^samurai-get-token/$', self.get_token, name="get_token"),)
        return urlpatterns
