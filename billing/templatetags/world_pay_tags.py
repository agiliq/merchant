'''
Template tags for WorldPay offsite payments
'''
from django import template
from django.template.loader import render_to_string
from billing.forms.world_pay_forms import WPHostedPaymentForm

class WorldPayNode(template.Node):
    def __init__(self, integration):
        self.integration = template.Variable(integration)

    def render(self, context):
        int_obj = self.integration.resolve(context)
        form_str = render_to_string("billing/world_pay.html", 
                                    {"form": WPHostedPaymentForm(initial=int_obj.fields),
                                     "integration": int_obj}, context)
        return form_str

def world_pay(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return WorldPayNode(int_obj)
