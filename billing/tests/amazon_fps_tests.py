from django.test import TestCase
from billing import get_integration
from django.template import Template, Context
from django.conf import settings

class AmazonFPSTestCase(TestCase):
    urls = "billing.tests.test_urls"

    def setUp(self):
        self.fps = get_integration("amazon_fps")
        fields = {
            "callerReference": "100",
            "paymentReason": "Digital Download",
            "pipelineName": "SingleUse",
            "transactionAmount": 30,
            "returnURLPrefix": "http://localhost",
            }
        self.fps.add_fields(fields)

    def testLinkGen(self):
        tmpl = Template("{% load billing_tags %}{% amazon_fps obj %}")
        link = tmpl.render(Context({"obj": self.fps}))
        pregen_link = """<a href="https://authorize.payments-sandbox.amazon.com/cobranded-ui/actions/start?callerKey=%(aws_access_key)s&callerReference=100&paymentReason=Digital%%20Download&pipelineName=SingleUse&returnURL=http%%3A%%2F%%2Flocalhost%%2Ffps%%2Ffps-return-url%%2F&signature=oSnkew7oCBPVk0IVZAjO87Ogsp4EO7jRlELaFwtqWzY%%3D&signatureMethod=HmacSHA256&signatureVersion=2&transactionAmount=30"><img src="http://g-ecx.images-amazon.com/images/G/01/cba/b/p3.gif" alt="Amazon Payments" /></a>""" %({"aws_access_key": settings.AWS_ACCESS_KEY})
        self.assertEquals(pregen_link, link.strip())
