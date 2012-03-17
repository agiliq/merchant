from django.test import TestCase
from billing import get_gateway, CreditCard
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa
from samurai.payment_method import PaymentMethod


class SamuraiGatewayTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("samurai")
        self.credit_card = CreditCard(first_name="Test", last_name="User",
                                      month=10, year=2012,
                                      number="4111111111111111",
                                      verification_value="100")

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

    def testStoreMissingCustomer(self):
        self.assertRaises(TypeError, self.merchant.store)

    def testCredit(self):
        resp = self.merchant.purchase(1000, self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        identification = resp["response"].reference_id
        resp = self.merchant.credit(money=100, identification=identification)
        self.assertEquals(resp["status"], "SUCCESS")

    def testAuthorizeAndCapture(self):
        resp = self.merchant.authorize(1000, self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        response = self.merchant.capture(50, resp["response"].reference_id)
        self.assertEquals(response["status"], "SUCCESS")

    def testStoreWithoutBillingAddress(self):
        resp = self.merchant.store(self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        self.assertEquals(resp["response"].expiry_month, self.credit_card.month)
        self.assertEquals(resp["response"].expiry_year, self.credit_card.year)
        self.assertTrue(getattr(resp["response"], "payment_method_token"))
        self.assertTrue(getattr(resp["response"], "created_at"))

    def testUnstore(self):
        resp = self.merchant.store(self.credit_card)
        self.assertEquals(resp["status"], "SUCCESS")
        response = self.merchant.unstore(resp["response"].payment_method_token)
        self.assertEquals(response["status"], "SUCCESS")

    def testPurchaseWithToken(self):
        resp = PaymentMethod.create('4111111111111111', '111', '07', '14')
        resp = self.merchant.purchase(500, resp.payment_method_token)
        self.assertEquals(resp["status"], "SUCCESS")
