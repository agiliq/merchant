import re
from urllib2 import urlparse

from django.test import TestCase
from django.template import Template, Context
from django.conf import settings

from billing import get_integration


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
        tmpl = Template("{% load amazon_fps from amazon_fps_tags %}{% amazon_fps obj %}")
        link = tmpl.render(Context({"obj": self.fps}))
        # get the integration link url
        url = re.search('href="(.*)">', link).groups()[0]
        parsed = urlparse.urlparse(url)
        query_dict = dict(urlparse.parse_qsl(parsed.query))

        self.assertEquals(parsed.scheme, 'https')
        self.assertEquals(parsed.netloc, 'authorize.payments-sandbox.amazon.com')
        self.assertEquals(parsed.path, '/cobranded-ui/actions/start')

        self.assertDictContainsSubset(self.fields, query_dict)
        self.assertEquals(query_dict['callerKey'], settings.MERCHANT_SETTINGS['amazon_fps']['AWS_ACCESS_KEY'])
