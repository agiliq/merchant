'''
Template tags for Braintree Payments Transparent Redirect
'''
from django import template
from django.template.loader import render_to_string
from billing.forms.braintree_payments_forms import BraintreePaymentsForm

class BraintreePaymentsNode(template.Node):
    def __init__(self, integration):
        self.integration = template.Variable(integration)

    def render(self, context):
        int_obj = self.integration.resolve(context)
        form_str = render_to_string("billing/braintree_payments.html", 
                                    {"form": BraintreePaymentsForm(int_obj),
                                     "integration": int_obj}, context)
        return form_str

def braintree_payments(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return BraintreePaymentsNode(int_obj)
