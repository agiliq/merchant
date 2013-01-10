'''
Template tags for Authorize.net Direct Post Method
'''
from django import template
from django.template.loader import render_to_string

register = template.Library()

class AuthorizeNetDPMNode(template.Node):
    def __init__(self, integration):
        self.integration = template.Variable(integration)

    def render(self, context):
        int_obj = self.integration.resolve(context)
        form_str = render_to_string("billing/authorize_net_dpm.html", 
                                    {"form": int_obj.generate_form(),
                                     "integration": int_obj}, context)
        return form_str

@register.tag
def authorize_net_dpm(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return AuthorizeNetDPMNode(int_obj)
