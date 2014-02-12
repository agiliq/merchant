import re

from django.test.utils import compare_xml
from lxml import etree


class BetterXMLCompareMixin(object):

    maxDiff = None

    def assertXMLEqual(self, expected, actual):
        if not compare_xml(actual, expected):
            self.assertMultiLineEqual(self.norm_whitespace(expected),
                                      self.norm_whitespace(actual))

    def norm_whitespace(self, v):
        v = re.sub(b"^ *", b"", v, flags=re.MULTILINE)
        v = re.sub(b"\n", b"", v)
        v = re.sub(b"\t", b"", v)
        return etree.tostring(etree.fromstring(v), pretty_print=True)

