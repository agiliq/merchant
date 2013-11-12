from django.test import TestCase
from billing import get_gateway, CreditCard
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa
from django.utils.unittest.case import skipIf
import stripe
from django.conf import settings

@skipIf(not settings.MERCHANT_SETTINGS.get("stripe", None), "gateway not configured")
class StripeGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("stripe")
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2020,
                                      number="4242424242424242",
                                      verification_value="100")
        stripe.api_key = self.merchant.stripe.api_key
        self.stripe = stripe

    def testCardSupported(self):
        self.credit_card.number = "5019222222222222"
        self.assertRaises(CardNotSupported,
                     lambda: self.merchant.purchase(1000, self.credit_card))

    def testCardType(self):
        self.credit_card.number = '4242424242424242'
        self.merchant.validate_card(self.credit_card)
        self.assertEquals(self.credit_card.card_type, Visa)

    def testPurchase(self):
        resp = self.merchant.purchase(1, self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")

    def testPurchaseDecimalAmount(self):
        resp = self.merchant.purchase(1.99, self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")

    def testStoreMissingCustomer(self):
        self.assertRaises(TypeError, self.merchant.store)

    def testStoreWithoutBillingAddress(self):
        resp = self.merchant.store(self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertEquals(resp["response"].active_card.exp_month, self.credit_card.month)
        self.assertEquals(resp["response"].active_card.exp_year, self.credit_card.year)
        self.assertTrue(getattr(resp["response"], "id"))
        self.assertTrue(getattr(resp["response"], "created"))

    def testUnstore(self):
        resp = self.merchant.store(self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        response = self.merchant.unstore(resp["response"].id)
        self.assertEquals(response["status"], "SUCCESS")

    def testRecurring1(self):
        plan_id = "test_plan"
        try:
            plan = self.stripe.Plan.retrieve(plan_id)
        except self.stripe.InvalidRequestError:
            response = self.stripe.Plan.create(
                amount=1000,
                interval='month',
                name="Test Plan",
                currency="usd",
                id=plan_id)
        options = {"plan_id": plan_id}
        resp = self.merchant.recurring(self.credit_card, options=options)
        self.assertEquals(resp["status"], "SUCCESS")
        subscription = resp["response"].subscription
        self.assertEquals(subscription.status, "active")

    def testCredit(self):
        resp = self.merchant.purchase(1, self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        identification = resp["response"].id
        resp = self.merchant.credit(identification=identification)
        self.assertEquals(resp["status"], "SUCCESS")

    def testAuthorizeAndCapture(self):
        resp = self.merchant.authorize(100, self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        response = self.merchant.capture(50, resp["response"].id)
        self.assertEquals(response["status"], "SUCCESS")

    def testPurchaseWithToken(self):
        # Somewhat similar to capture but testing for the
        # purpose of the stripe integration
        resp = self.merchant.authorize(1, self.credit_card)
        resp = self.merchant.purchase(1, resp["response"].id)
        self.assertEquals(resp["status"], "SUCCESS")
