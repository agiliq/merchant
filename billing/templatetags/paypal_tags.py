'''
Template tags for paypal offsite payments
'''
from paypal.standard.forms import PayPalPaymentsForm, PayPalEncryptedPaymentsForm
from django import template
from django.template.loader import render_to_string

register = template.Library()

class PayPalNode(template.Node):
    def __init__(self, integration, encrypted=False):
        self.integration = template.Variable(integration)
        self.encrypted = encrypted

    def render(self, context):
        int_obj = self.integration.resolve(context)
        if self.encrypted:
            form_class = PayPalEncryptedPaymentsForm
        else:
            form_class = PayPalPaymentsForm
        form_str = render_to_string("billing/paypal.html", 
                                    {"form": form_class(initial=int_obj.fields),
                                     "integration": int_obj}, context)
        return form_str


@register.tag
def paypal(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return PayPalNode(int_obj)


@register.tag
def paypal_encrypted(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return PayPalNode(int_obj, encrypted=True)
