from coffin.template import Library
from django.template.loader import render_to_string
from jinja2 import nodes
from jinja2.ext import Extension


register = Library()


class MerchantExtension(Extension):

    tags = set(['render_integration'])

    def parse(self, parser):
        stream = parser.stream
        lineno = stream.next().lineno

        obj = parser.parse_expression()
        call_node = self.call_method('render_integration', args=[obj])

        return nodes.Output([call_node]).set_lineno(lineno)

    @classmethod
    def render_integration(self, obj):
        form_str = render_to_string(obj.template, {'integration': obj})
        return form_str

register.tag(MerchantExtension)
