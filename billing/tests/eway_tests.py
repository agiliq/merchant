from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing import get_gateway, CreditCard
from billing.signals import *
from billing.models import EwayResponse
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa

fake_options = {
    "email": "testuser@fakedomain.com",
    "billing_address": {
        "name": "PayPal User",
        "address1": "Street 1",
        "city": "Mountain View",
        "state": "CA",
        "country": "US",
        "zip": "94043",
        "fax": "1234567890",
        "email": "testuser@fakedomain.com",
        "phone": "1234567890",
        "mobile": "1234567890",
        "customer_ref": "Blah",
        "job_desc": "Job",
        "comments": "comments",
        "url": "http://google.com.au/",
    },
    "invoice": "1234",
    "description": "Blah Blah!",
    "customer_details": {
        "customer_fname": "TEST",
        "customer_lname": "USER",
        "customer_address": "#43, abc",
        "customer_email": "abc@test.Com",
        "customer_postcode": 560041,
    },
    "payment_details": {
        "amount": 100,  # In cents
        "transaction_number": 3234,
        "inv_ref": 'REF1234',
        "inv_desc": "Please Ship ASASP",
    }
}

@skipIf(not settings.MERCHANT_SETTINGS.get("eway", None), "gateway not configured")
class EWayGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("eway")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2020,
                                      number="4444333322221111",
                                      verification_value="100")

    def testCardSupported(self):
        self.credit_card.number = "5019222222222222"
        self.assertRaises(CardNotSupported,
                          lambda: self.merchant.purchase(1000, self.credit_card))

    def testCardValidated(self):
        self.merchant.test_mode = False
        self.credit_card.number = "4222222222222123"
        self.assertFalse(self.merchant.validate_card(self.credit_card))

    def testCardType(self):
        self.merchant.validate_card(self.credit_card)
        self.assertEquals(self.credit_card.card_type, Visa)

    def testPurchase(self):
        resp = self.merchant.purchase(100, self.credit_card,
                                      options=fake_options)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertNotEquals(resp["response"].ewayTrxnStatus, True)
        self.assertEquals(resp["response"].ewayTrxnError,
                          "00,Transaction Approved(Test Gateway)")
        self.assertNotEquals(resp["response"].ewayTrxnNumber, "0")
        self.assertTrue(resp["response"].ewayReturnAmount, "100")

    def testFailure(self):
        resp = self.merchant.purchase(105, self.credit_card,
                                      options=fake_options)
        self.assertEquals(resp["status"], "FAILURE")
        self.assertEquals(resp["response"].ewayTrxnError,
                          "05,Do Not Honour(Test Gateway)")
        self.assertNotEquals(resp["response"].ewayTrxnNumber, "0")
        self.assertTrue(resp["response"].ewayReturnAmount, "100")

    def testDirectPayment(self):
        credit_card_details = {
            'first_name': 'test fname',
            'last_name': 'test lname',
            'verification_value': '123',
            'number': '4444333322221111',
            'month': '7',
            'card_type': 'visa',
            'year': '2017'
        }
        resp = self.merchant.direct_payment(credit_card_details,
                                            options=fake_options)
        self.assertEquals(resp["status"], "SUCCESS")
        eway_response = resp["response"]["ewayResponse"]
        self.assertEquals(eway_response['ewayTrxnStatus'], 'True')
        self.assertEquals(eway_response["ewayReturnAmount"], "100")

    def testPaymentSuccessfulSignal(self):
        # Since in the test mode, all transactions are
        # failures, we need to be checking for transaction_was_unsuccessful
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(1, self.credit_card,
                                      options=fake_options)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(6, self.credit_card,
                                      options=fake_options)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testCreditCardExpired(self):
        resp = self.merchant.purchase(8, self.credit_card,
                                      options=fake_options)
        self.assertNotEquals(resp["status"], "SUCCESS")
