from django import forms

from billing.forms.authorize_net_forms import AuthorizeNetDPMForm as BaseAuthorizeNetDPMForm
from billing.integrations.authorize_net_dpm_integration import AuthorizeNetDpmIntegration as BaseAuthorizeNetDpmIntegration


class AuthorizeNetDPMForm(BaseAuthorizeNetDPMForm):
    x_cust_id = forms.CharField(max_length=20, label="Customer ID", required=False)


class AuthorizeNetDpmIntegration(BaseAuthorizeNetDpmIntegration):

    def form_class(self):
        return AuthorizeNetDPMForm
