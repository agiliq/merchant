from billing.integrations.stripe_integration import StripeIntegration
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class StripeExampleIntegration(StripeIntegration):
    def transaction(self, request):
        resp = self.gateway.purchase(100, request.POST["stripeToken"])
        return HttpResponseRedirect("%s?status=%s" %(reverse("app_offsite_stripe"),
                                                     resp["status"]))
