import braintree

from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing import get_gateway, CreditCard
from billing.signals import *
from billing.gateway import CardNotSupported, InvalidData
from billing.utils.credit_card import Visa


@skipIf(not settings.MERCHANT_SETTINGS.get("braintree_payments", None), "gateway not configured")
class BraintreePaymentsGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("braintree_payments")
        self.merchant.test_mode = True
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2020,
                                      number="4111111111111111",
                                      verification_value="100")

    def assertBraintreeResponseSuccess(self, resp, msg=None):
        if resp['status'] == "FAILURE":
            standardMsg = resp['response'].message
            self.fail(self._formatMessage(msg, standardMsg))
        else:
            self.assertEquals(resp['status'], "SUCCESS")

    def assertBraintreeResponseFailure(self, resp, msg=None):
        self.assertEquals(resp['status'], "FAILURE")

    def testCardSupported(self):
        self.credit_card.number = "5019222222222222"
        self.assertRaises(CardNotSupported,
                          lambda: self.merchant.purchase(1000, self.credit_card))

    def testCardType(self):
        self.merchant.validate_card(self.credit_card)
        self.assertEquals(self.credit_card.card_type, Visa)

    def testPurchase(self):
        resp = self.merchant.purchase(5, self.credit_card)
        self.assertBraintreeResponseSuccess(resp)

    def testFailedPurchase(self):
        resp = self.merchant.purchase(2001, self.credit_card)
        self.assertBraintreeResponseFailure(resp)

    def testDeclinedPurchase(self):
        resp = self.merchant.purchase(2900, self.credit_card)
        self.assertBraintreeResponseFailure(resp)

    def testPaymentSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_successful.connect(receive)

        resp = self.merchant.purchase(1, self.credit_card)
        self.assertEquals(received_signals, [transaction_was_successful])

    def testPaymentUnSuccessfulSignal(self):
        received_signals = []

        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        transaction_was_unsuccessful.connect(receive)

        resp = self.merchant.purchase(2000, self.credit_card)
        self.assertEquals(received_signals, [transaction_was_unsuccessful])

    def testCreditCardExpired(self):
        credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2011,
                                 number="4000111111111115",
                                 verification_value="100")
        resp = self.merchant.purchase(2004, credit_card)
        self.assertNotEquals(resp["status"], "SUCCESS")

    def testAuthorizeAndCapture(self):
        resp = self.merchant.authorize(100, self.credit_card)
        self.assertBraintreeResponseSuccess(resp)
        resp = self.merchant.capture(50, resp["response"].transaction.id)
        self.assertBraintreeResponseSuccess(resp)

    # Need a way to test this. Requires delaying the status to either
    # "settled" or "settling"
    # def testAuthorizeAndRefund(self):
    #     resp = self.merchant.purchase(100, self.credit_card)
    #     self.assertEquals(resp["status"], "SUCCESS")
    #     response = self.merchant.credit(50, resp["response"].transaction.id)
    #     self.assertEquals(response["status"], "SUCCESS")

    def testAuthorizeAndVoid(self):
        resp = self.merchant.authorize(105, self.credit_card)
        self.assertBraintreeResponseSuccess(resp)
        resp = self.merchant.void(resp["response"].transaction.id)
        self.assertBraintreeResponseSuccess(resp)

    def testStoreMissingCustomer(self):
        self.assertRaises(InvalidData,
                          lambda: self.merchant.store(self.credit_card, {}))

    def testStoreWithoutBillingAddress(self):
        options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            }
        resp = self.merchant.store(self.credit_card, options=options)
        self.assertBraintreeResponseSuccess(resp)
        self.assertEquals(resp["response"].customer.credit_cards[0].expiration_date,
                          "%s/%s" % (self.credit_card.month,
                                    self.credit_card.year))
        self.assertTrue(getattr(resp["response"].customer.credit_cards[0], "customer_id"))
        self.assertTrue(getattr(resp["response"].customer.credit_cards[0], "token"))

    def testStoreWithBillingAddress(self):
        options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            "billing_address": {
                "name": "Johnny Doe",
                "company": "",
                "email": "johnny.doe@example.com",
                "address1": "Street #1",
                "address2": "House #2",
                "city": "Timbuktu",
                "country": "United States of America",
                "zip": "110011"
                }
            }
        resp = self.merchant.store(self.credit_card, options=options)
        self.assertBraintreeResponseSuccess(resp)
        self.assertTrue(getattr(resp["response"].customer.credit_cards[0], "billing_address"))
        billing_address = resp["response"].customer.credit_cards[0].billing_address
        self.assertEquals(billing_address.country_code_alpha2, "US")
        self.assertEquals(billing_address.postal_code, "110011")
        self.assertEquals(billing_address.street_address, "Street #1")
        self.assertEquals(billing_address.extended_address, "House #2")
        self.assertEquals(billing_address.locality, "Timbuktu")

    def testUnstore(self):
        options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            }
        resp = self.merchant.store(self.credit_card, options=options)
        self.assertBraintreeResponseSuccess(resp)
        resp = self.merchant.unstore(resp["response"].customer.credit_cards[0].token)
        self.assertBraintreeResponseSuccess(resp)

    # The below tests require 'test_plan' to be created in the sandbox
    # console panel. This cannot be created by API at the moment
    def testRecurring1(self):
        options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            "recurring": {
                "plan_id": "test_plan"
                },
            }
        resp = self.merchant.recurring(10, self.credit_card, options=options)
        self.assertBraintreeResponseSuccess(resp)
        subscription = resp["response"].subscription
        self.assertEquals(subscription.status,
                          braintree.Subscription.Status.Active)

    def testRecurring2(self):
        options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            "recurring": {
                "plan_id": "test_plan",
                "price": 15
                },
            }
        resp = self.merchant.recurring(15, self.credit_card, options=options)
        self.assertBraintreeResponseSuccess(resp)
        subscription = resp["response"].subscription
        self.assertEquals(subscription.price, 15)

    def testRecurring3(self):
        options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            "recurring": {
                "plan_id": "test_plan",
                "trial_duration": 2,
                "trial_duration_unit": "month",
                "number_of_billing_cycles": 12,
                },
            }
        resp = self.merchant.recurring(20, self.credit_card, options=options)
        self.assertBraintreeResponseSuccess(resp)
        subscription = resp["response"].subscription
        self.assertEquals(subscription.number_of_billing_cycles, 12)
