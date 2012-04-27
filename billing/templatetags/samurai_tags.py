'''
Template tags for Samurai Non PCI Complaince
'''
from django import template
from django.template.loader import render_to_string
from billing.forms.samurai_forms import SamuraiForm

register = template.Library()

class SamuraiNode(template.Node):
    def __init__(self, integration):
        self.integration = template.Variable(integration)

    def render(self, context):
        int_obj = self.integration.resolve(context)
        form_str = render_to_string("billing/samurai.html", 
                                    {"form":SamuraiForm(int_obj),
                                     "integration": int_obj}, context)
        return form_str

@register.tag
def samurai_payment(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return SamuraiNode(int_obj)
