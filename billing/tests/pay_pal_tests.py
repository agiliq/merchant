from django.test import TestCase
from billing import get_gateway, get_integration, CreditCard
from billing.signals import *
from paypal.pro.models import PayPalNVP
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa
from paypal.pro.tests import RequestFactory
from django.template import Template, Context
from django.utils.html import strip_spaces_between_tags
from django.core.urlresolvers import reverse
import datetime

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
    # "shipping_address": {
    #     "name": "PayPal User",
    #     "address1": "Street 1",
    #     "city": "Mountain View",
    #     "state": "CA",
    #     "country": "US",
    #     "zip": "94043"
    #     },
}

class PayPalGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("pay_pal")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2011, 
                                      number="4500775008976759", 
                                      verification_value="000")

    def testCardSupported(self):
        self.credit_card.number = "5019222222222222"
        self.assertRaises(CardNotSupported, 
                          lambda : self.merchant.purchase(1000, self.credit_card))

    def testCardValidated(self):
        self.merchant.test_mode = False
        self.credit_card.number = "4222222222222123"
        self.assertFalse(self.merchant.validate_card(self.credit_card))

    def testCardType(self):
        self.merchant.validate_card(self.credit_card)
        self.assertEquals(self.credit_card.card_type, Visa)

    def testPurchase(self):
        resp = self.merchant.purchase(1, self.credit_card, 
                                      options = fake_options)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertNotEquals(resp["response"].correlationid, "0")
        self.assertTrue(isinstance(resp["response"], PayPalNVP)) 

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        resp = self.merchant.purchase(1, self.credit_card,
                                      options = fake_options)
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(105.02, self.credit_card,
                                      options = fake_options)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testCreditCardExpired(self):
        resp = self.merchant.purchase(105.02, self.credit_card,
                                      options = fake_options)
        self.assertNotEquals(resp["status"], "SUCCESS")


class PayPalWebsiteStandardsTestCase(TestCase):
    urls = "billing.tests.test_urls"

    def setUp(self):
        self.today = datetime.datetime.today().strftime("%Y-%m-%d")
        self.pws = get_integration("pay_pal")
        self.pws.test_mode = True
        fields = {"cmd": "_xclick",
        'notify_url': 'http://localhost/paypal-ipn-handler/',
        'return_url': 'http://localhost/offsite/paypal/done/',
        'cancel_return': 'http://localhost/offsite/paypal/',
        'amount': 1,
        'item_name': "Test Item",
        'invoice': self.today,}
        self.pws.add_fields(fields)

    def testRenderForm(self):
        tmpl = Template("{% load billing_tags %}{% paypal obj %}")
        form = tmpl.render(Context({"obj": self.pws}))
        pregen_form = """<form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post"><input type="hidden" name="business" value="probiz_1273571007_biz@uswaretech.com" id="id_business" /><input type="hidden" name="amount" value="1" id="id_amount" /><input type="hidden" name="item_name" value="Test Item" id="id_item_name" /><input type="hidden" name="notify_url" value="http://localhost/paypal-ipn-handler/" id="id_notify_url" /><input type="hidden" name="cancel_return" value="http://localhost/offsite/paypal/" id="id_cancel_return" /><input type="hidden" name="return" value="http://localhost/offsite/paypal/done/" id="id_return_url" /><input type="hidden" name="invoice" value="%(today)s" id="id_invoice" /><input type="hidden" name="cmd" value="_xclick" id="id_cmd" /><input type="hidden" name="charset" value="utf-8" id="id_charset" /><input type="hidden" name="currency_code" value="USD" id="id_currency_code" /><input type="hidden" name="no_shipping" value="1" id="id_no_shipping" /><input type="image" src="https://www.sandbox.paypal.com/en_US/i/btn/btn_buynowCC_LG.gif" border="0" name="submit" alt="Buy it Now" /></form>""" % ( {"today": self.today} )
        self.assertEquals(pregen_form, strip_spaces_between_tags(form).strip())

    def testIPNURLSetup(self):
        self.assertEquals(reverse("paypal-ipn"), "/paypal-ipn-url/")
