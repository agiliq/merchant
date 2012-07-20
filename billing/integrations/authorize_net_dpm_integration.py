from billing import Integration, IntegrationNotConfigured
from billing.forms.authorize_net_forms import AuthorizeNetDPMForm
from django.conf import settings
from django.conf.urls.defaults import patterns, url
import hashlib
import hmac

class AuthorizeNetDpmIntegration(Integration):
    display_name = "Authorize.Net Direct Post Method"

    def __init__(self):
        super(AuthorizeNetDpmIntegration, self).__init__()
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("authorize_net"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                           "configured." % self.display_name)
        authorize_net_settings = merchant_settings["authorize_net"]

    def generate_form(self):
        authorize_net_settings = settings.MERCHANT_SETTINGS["authorize_net"]
        transaction_key = authorize_net_settings["TRANSACTION_KEY"]
        login_id = authorize_net_settings["LOGIN_ID"]

        initial_data = self.fields 
        x_fp_hash = hmac.new(transaction_key, "%s^%s^%s^%s^" %(login_id, 
                                                               initial_data['x_fp_sequence'], 
                                                               initial_data['x_fp_timestamp'], 
                                                               initial_data['x_amount']),
                             hashlib.md5)
        initial_data.update({'x_login': login_id, 
                             'x_fp_hash': x_fp_hash.hexdigest()})
        form = AuthorizeNetDPMForm(initial=initial_data)
        return form

    @property
    def service_url(self):
        if self.test_mode:
            return "https://test.authorize.net/gateway/transact.dll"
        return "https://secure.authorize.net/gateway/transact.dll"

    def authorizenet_notify_handler(self, request):
        result = {}
        if result.is_success:
            transaction_was_successful.send(sender=self,
                                            type="sale",
                                            response=result)
            return self.authorize_net_success_handler(request, result)
        transaction_was_unsuccessful.send(sender=self,
                                          type="sale",
                                          response=result)
        return self.authorize_net_failure_handler(request, result)

    def authorize_net_success_handler(self, request, response):
        return render_to_response("billing/authorize_net_success.html", 
                                  {"response": response},
                                  context_instance=RequestContext(request))

    def authorize_net_failure_handler(self, request, response):
        return render_to_response("billing/authorize_net_failure.html", 
                                  {"response": response},
                                  context_instance=RequestContext(request))

    def get_urls(self):
        urlpatterns = patterns('',
           url('^authorize_net-notify-handler/$', self.authorizenet_notify_handler, name="authorize_net_notify_handler"),)
        return urlpatterns

