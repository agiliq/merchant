from xml.dom import minidom
from urllib2 import urlparse

from django.conf import settings
from django.test import TestCase
from django.template import Template, Context
from django.utils.unittest.case import skipIf

from billing import get_integration


@skipIf(not settings.MERCHANT_SETTINGS.get("amazon_fps", None), "gateway not configured")
class AmazonFPSTestCase(TestCase):
    urls = "billing.tests.test_urls"

    def setUp(self):
        self.fps = get_integration("amazon_fps")
        self.fields = {
            "callerReference": "100",
            "paymentReason": "Digital Download",
            "pipelineName": "SingleUse",
            "transactionAmount": '30',
            "returnURL": "http://localhost/fps/fps-return-url/",
        }
        self.fps.add_fields(self.fields)

    def testLinkGen(self):
        tmpl = Template("{% load render_integration from billing_tags %}{% render_integration obj %}")
        html = tmpl.render(Context({"obj": self.fps}))
        # get the integration link url
        dom = minidom.parseString(html)
        url = dom.getElementsByTagName('a')[0].attributes['href'].value
        parsed = urlparse.urlparse(url)
        query_dict = dict(urlparse.parse_qsl(parsed.query))

        self.assertEquals(parsed.scheme, 'https')
        self.assertEquals(parsed.netloc, 'authorize.payments-sandbox.amazon.com')
        self.assertEquals(parsed.path, '/cobranded-ui/actions/start')

        self.assertDictContainsSubset(self.fields, query_dict)
        self.assertEquals(query_dict['callerKey'], settings.MERCHANT_SETTINGS['amazon_fps']['AWS_ACCESS_KEY'])
