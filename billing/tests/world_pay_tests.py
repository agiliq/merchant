from urllib2 import urlparse
from xml.dom import minidom

from django.test import TestCase
from django.template import Template, Context
from django.conf import settings

from billing import get_integration


class WorldPayTestCase(TestCase):
    def setUp(self):
        self.wp = get_integration("world_pay")
        fields = {
            "cartId": "TEST123",
            "amount": "1",
            "currency": "USD",
            "testMode": "100",
            "futurePayType": "regular",
            "option": "0",
            "noOfPayments": "12",
            "intervalUnit": "3",
            "intervalMult": "1",
            "normalAmount": "1",
            "startDelayUnit": "3",
            "startDelayMult": "1",
            "instId": "12345",
            "signatureFields": "instId:amount:cartId",
        }
        self.wp.add_fields(fields)

    def assertFormIsCorrect(self, form, fields):
        dom = minidom.parseString(form)
        inputs = dom.getElementsByTagName('input')
        values_dict = {}
        for el in inputs:
            if el.attributes['type'].value == 'hidden' and el.hasAttribute('value'):
                values_dict[el.attributes['name'].value] = el.attributes['value'].value
        self.assertDictContainsSubset(values_dict, fields)

        form_action_url = dom.getElementsByTagName('form')[0].attributes['action'].value
        parsed = urlparse.urlparse(form_action_url)

        self.assertEquals(parsed.scheme, 'https')
        self.assertEquals(parsed.netloc, 'select-test.worldpay.com')
        self.assertEquals(parsed.path, '/wcc/purchase')

    def testFormGen(self):
        # Since the secret key cannot be distributed
        settings.WORLDPAY_MD5_SECRET_KEY = "test"
        tmpl = Template("{% load render_integration from billing_tags %}{% render_integration obj %}")
        form = tmpl.render(Context({"obj": self.wp}))
        self.assertFormIsCorrect(form, self.wp.fields)

    def testFormGen2(self):
        # Since the secret key cannot be distributed
        settings.WORLDPAY_MD5_SECRET_KEY = "test"
        self.wp.add_field("signatureFields", "instId:amount:currency:cartId")
        self.wp.fields.pop("signature", None)
        tmpl = Template("{% load render_integration from billing_tags %}{% render_integration obj %}")
        form = tmpl.render(Context({"obj": self.wp}))
        self.assertFormIsCorrect(form, self.wp.fields)
