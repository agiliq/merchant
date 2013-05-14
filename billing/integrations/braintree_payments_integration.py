from billing import Integration, IntegrationNotConfigured
from django.conf import settings
from django.views.decorators.http import require_GET
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from django.conf.urls import patterns, url
import braintree
import urllib
from django.core.urlresolvers import reverse
from billing.forms.braintree_payments_forms import BraintreePaymentsForm
from django.shortcuts import render_to_response
from django.template import RequestContext


class BraintreePaymentsIntegration(Integration):
    display_name = "Braintree Transparent Redirect"
    template = "billing/braintree_payments.html"

    def __init__(self, options=None):
        if not options:
            options = {}
        super(BraintreePaymentsIntegration, self).__init__(options=options)

        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("braintree_payments"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        braintree_payments_settings = merchant_settings["braintree_payments"]
        test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)
        if test_mode:
            env = braintree.Environment.Sandbox
        else:
            env = braintree.Environment.Production
        braintree.Configuration.configure(
            env,
            braintree_payments_settings['MERCHANT_ACCOUNT_ID'],
            braintree_payments_settings['PUBLIC_KEY'],
            braintree_payments_settings['PRIVATE_KEY']
            )

    @property
    def service_url(self):
        return braintree.TransparentRedirect.url()

    def braintree_notify_handler(self, request):
        fpath = request.get_full_path()
        query_string = fpath.split("?", 1)[1]
        result = braintree.TransparentRedirect.confirm(query_string)
        if result.is_success:
            transaction_was_successful.send(sender=self,
                                            type="sale",
                                            response=result)
            return self.braintree_success_handler(request, result)
        transaction_was_unsuccessful.send(sender=self,
                                          type="sale",
                                          response=result)
        return self.braintree_failure_handler(request, result)

    def braintree_success_handler(self, request, response):
        return render_to_response("billing/braintree_success.html",
                                  {"response": response},
                                  context_instance=RequestContext(request))

    def braintree_failure_handler(self, request, response):
        return render_to_response("billing/braintree_failure.html",
                                  {"response": response},
                                  context_instance=RequestContext(request))

    def get_urls(self):
        urlpatterns = patterns('',
           url('^braintree-notify-handler/$', self.braintree_notify_handler, name="braintree_notify_handler"),)
        return urlpatterns

    def add_fields(self, params):
        for (key, val) in params.iteritems():
            if isinstance(val, dict):
                new_params = {}
                for k in val:
                    new_params["%s__%s" % (key, k)] = val[k]
                self.add_fields(new_params)
            else:
                self.add_field(key, val)

    def generate_tr_data(self):
        tr_data_dict = {"transaction": {}}
        tr_data_dict["transaction"]["type"] = self.fields["transaction__type"]
        tr_data_dict["transaction"]["order_id"] = self.fields["transaction__order_id"]
        if self.fields.get("transaction__customer_id"):
            tr_data_dict["transaction"]["customer_id"] = self.fields["transaction__customer__id"]
        if self.fields.get("transaction__customer__id"):
            tr_data_dict["transaction"]["customer"] = {"id": self.fields["transaction__customer__id"]}
        tr_data_dict["transaction"]["options"] = {"submit_for_settlement":
                                                  self.fields.get("transaction__options__submit_for_settlement", True)}
        if self.fields.get("transaction__payment_method_token"):
            tr_data_dict["transaction"]["payment_method_token"] = self.fields["transaction__payment_method_token"]
        if self.fields.get("transaction__credit_card__token"):
            tr_data_dict["transaction"]["credit_card"] = {"token": self.fields["transaction__credit_card__token"]}
        if self.fields.get("transaction__amount"):
            tr_data_dict["transaction"]["amount"] = self.fields["transaction__amount"]
        notification_url = "%s%s" % (self.fields["site"], reverse("braintree_notify_handler"))
        tr_data = braintree.Transaction.tr_data_for_sale(tr_data_dict, notification_url)
        return tr_data

    def form_class(self):
        return BraintreePaymentsForm

    def generate_form(self):
        initial_data = self.fields
        initial_data.update({"tr_data": self.generate_tr_data()})
        form = self.form_class()(initial=initial_data)
        return form
