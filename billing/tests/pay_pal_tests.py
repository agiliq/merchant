import datetime
from urllib2 import urlparse
from xml.dom import minidom

from django.conf import settings
from django.test.client import RequestFactory
from django.template import Template, Context
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.unittest.case import skipIf

from paypal.pro.models import PayPalNVP

from billing import get_gateway, get_integration, CreditCard
from billing.signals import *
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa

RF = RequestFactory()
request = RF.get("/", REMOTE_ADDR="192.168.1.1")
fake_options = {
    "request": request,
    "email": "testuser@fakedomain.com",
    "billing_address": {
        "name": "PayPal User",
        "address1": "Street 1",
        "city": "Mountain View",
        "state": "CA",
        "country": "US",
        "zip": "94043"
    },
}

@skipIf(not settings.MERCHANT_SETTINGS.get("pay_pal", None), "gateway not configured")
class PayPalGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("pay_pal")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2017,
                                      number="4500775008976759",
                                      verification_value="000")

    def testCardSupported(self):
        self.credit_card.number = "5019222222222222"
        self.assertRaises(CardNotSupported,
                          lambda: self.merchant.purchase(1000,
                                                         self.credit_card))

    def testCardValidated(self):
        self.merchant.test_mode = False
        self.credit_card.number = "4222222222222123"
        self.assertFalse(self.merchant.validate_card(self.credit_card))

    def testCardType(self):
        self.merchant.validate_card(self.credit_card)
        self.assertEquals(self.credit_card.card_type, Visa)

    def testPurchase(self):
        resp = self.merchant.purchase(1, self.credit_card,
                                      options=fake_options)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertNotEquals(resp["response"].correlationid, "0")
        self.assertTrue(isinstance(resp["response"], PayPalNVP))

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        resp = self.merchant.purchase(1, self.credit_card,
                                      options=fake_options)
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(105.02, self.credit_card,
                                      options=fake_options)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testCreditCardExpired(self):
        resp = self.merchant.purchase(105.02, self.credit_card,
                                      options=fake_options)
        self.assertNotEquals(resp["status"], "SUCCESS")


@skipIf(not settings.MERCHANT_SETTINGS.get("pay_pal", None), "gateway not configured")
class PayPalWebsiteStandardsTestCase(TestCase):
    urls = "billing.tests.test_urls"

    def setUp(self):
        self.today = datetime.datetime.today().strftime("%Y-%m-%d")
        self.pws = get_integration("pay_pal")
        self.pws.test_mode = True
        fields = {
            "cmd": "_xclick",
            'notify_url': 'http://localhost/paypal-ipn-handler/',
            'return_url': 'http://localhost/offsite/paypal/done/',
            'cancel_return': 'http://localhost/offsite/paypal/',
            'amount': '1',
            'item_name': "Test Item",
            'invoice': self.today,
        }
        self.pws.add_fields(fields)

    def assertFormIsCorrect(self, form, fields):
        dom = minidom.parseString(form)
        inputs = dom.getElementsByTagName('input')
        values_dict = {}
        for el in inputs:
            if (el.attributes['type'].value == 'hidden'
                    and el.hasAttribute('value')):
                values_dict[el.attributes['name'].value] = el.attributes['value'].value
        self.assertDictContainsSubset(values_dict, fields)

        form_action_url = dom.getElementsByTagName('form')[0].attributes['action'].value
        parsed = urlparse.urlparse(form_action_url)

        self.assertEquals(parsed.scheme, 'https')
        self.assertEquals(parsed.netloc, 'www.sandbox.paypal.com')
        self.assertEquals(parsed.path, '/cgi-bin/webscr')

    def testRenderForm(self):
        tmpl = Template("""
            {% load render_integration from billing_tags %}
            {% render_integration obj %}
        """)
        form = tmpl.render(Context({"obj": self.pws}))
        fields = self.pws.fields.copy()
        fields.update({
            'charset': 'utf-8',
            'currency_code': 'USD',
            'return': 'http://localhost/offsite/paypal/done/',
            'no_shipping': '1',
        })
        self.assertFormIsCorrect(form, fields)

    def testRenderFormMultipleItems(self):
        fields = self.pws.fields.copy()
        fields.update({
            'amount_1': '10',
            'item_name_1': 'Test Item 1',
            'amount_2': '20',
            'item_name_2': 'Test Item 2',
            'charset': 'utf-8',
            'currency_code': 'USD',
            'return': 'http://localhost/offsite/paypal/done/',
            'no_shipping': '1',
        })
        tmpl = Template("""
            {% load render_integration from billing_tags %}
            {% render_integration obj %}
        """)
        form = tmpl.render(Context({"obj": self.pws}))
        self.assertFormIsCorrect(form, fields)

    def testIPNURLSetup(self):
        self.assertEquals(reverse("paypal-ipn"), "/paypal-ipn-url/")
