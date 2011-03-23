'''
Template tags for Amazon FPS offsite payments
'''
from django import template
from django.template.loader import render_to_string

class AmazonFPSNode(template.Node):
    def __init__(self, integration):
        self.integration = template.Variable(integration)

    def render(self, context):
        int_obj = self.integration.resolve(context)
        form_str = render_to_string("billing/amazon_fps.html", 
                                    {"form": "",
                                     "integration": int_obj}, context)
        return form_str

def amazon_fps(parser, token):
    try:
        tag, int_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r was expecting a single argument" %token.split_contents()[0])
    return AmazonFPSNode(int_obj)
