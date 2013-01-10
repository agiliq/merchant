'''
Template tags for eWAY
'''
from django import template
from django.template.loader import render_to_string


register = template.Library()


class EwayNode(template.Node):
    def __init__(self, integration):
        self.integration = integration

    def render(self, context):
        return render_to_string("billing/eway.html",
                                {"integration": self.integration.resolve(context)},
                                context)


@register.tag
def eway(parser, token):
    bits = token.split_contents()
    try:
        integration = parser.compile_filter(bits[1])
    except (ValueError, IndexError):
        raise template.TemplateSyntaxError("%r expects a single argument" % bits[0])
    return EwayNode(integration)
