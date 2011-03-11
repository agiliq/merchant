'''
Template tags for google checkout offsite payments
'''
from paypal.standard.forms import PayPalPaymentsForm
from django import template
from django.template.loader import render_to_string

class GoogleCheckoutNode(template.Node):
    def __init__(self, integration):
        self.integration = template.Variable(integration)

    def render(self, context):
        int_obj = self.integration.resolve(context)
        form_str = render_to_string("billing/google_checkout.html", 
                                    {"integration": int_obj}, 
                                    context)
        return form_str

def google_checkout(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return GoogleCheckoutNode(int_obj)
