'''
Template tags for paypal offsite payments
'''
from django import template
from django.template.loader import render_to_string

register = template.Library()

class PayPalNode(template.Node):
    def __init__(self, integration, encrypted=False):
        self.integration = template.Variable(integration)
        self.encrypted = encrypted

    def render(self, context):
        int_obj = self.integration.resolve(context)
        form_str = render_to_string("billing/paypal.html", 
                                    {"form": int_obj.generate_form(),
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
