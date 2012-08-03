from datetime import date
from django.test import TestCase
from billing import get_gateway, CreditCard
from billing.signals import *
from billing.models import AuthorizeAIMResponse
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa

from beanstream.billing import Address

class BeanstreamGatewayTestCase(TestCase):
    approved_cards = {'visa': {'number':      '4030000010001234', 'cvd': '123'},
                       '100_visa': {'number': '4504481742333', 'cvd': '123'},
                       'vbv_visa': {'nubmer': '4123450131003312', 'cvd': '123', 'vbv': '12345'},
                       'mc1': {'number': '5100000010001004', 'cvd': '123'},
                       'mc2': {'number': '5194930004875020', 'cvd': '123'},
                       'mc3': {'number': '5123450000002889', 'cvd': '123'},
                       '3d_mc': {'number': '5123450000000000', 'cvd': '123', 'passcode': '12345'},
                       'amex': {'number': '371100001000131', 'cvd': '1234'},
                       'discover': {'number': '6011500080009080', 'cvd': '123'},
                      }
    declined_cards = {'visa': {'number': '4003050500040005', 'cvd': '123'},
                       'mc': {'number': '5100000020002000', 'cvd': '123'},
                       'amex': {'number': '342400001000180', 'cvd': '1234'},
                       'discover': {'number': '6011000900901111', 'cvd': '123'},
                      }

    def setUp(self):
        self.merchant = get_gateway("beanstream", **{"merchant_id": 267390000,
                                                     "hashcode"  : "dine-otestkey",
                                                     "hash_algorithm"   : "SHA1",
                                                     "payment_profile_passcode":"BCCE75A688F8497E9CDBC77AA8178581",
                                                })
        self.merchant.test_mode = True
        self.billing_address = Address(
            'John Doe',
            'john.doe@example.com',
            '555-555-5555',
            '123 Fake Street',
            '',
            'Fake City',
            'ON',
            'A1A1A1',
            'CA')

    def ccFactory(self, number, cvd):
        today = date.today()
        return CreditCard(first_name = "John",
                          last_name = "Doe",
                          month = str(today.month),
                          year = str(today.year + 1),
                          number = number,
                          verification_value = cvd)

    def testCardSupported(self):
        credit_card = self.ccFactory("5019222222222222", "100")
        self.assertRaises(CardNotSupported, 
                          lambda : self.merchant.purchase(1000, credit_card))

    def testCardValidated(self):
        self.merchant.test_mode = False
        credit_card = self.ccFactory("4222222222222123", "100")
        self.assertFalse(self.merchant.validate_card(credit_card))

    def testCardType(self):
        credit_card = self.ccFactory("4222222222222", "100")
        self.merchant.validate_card(credit_card)
        self.assertEquals(credit_card.card_type, Visa)

    def testCreditCardExpired(self):
        credit_card = CreditCard(first_name="John",
                          last_name="Doe",
                          month=12, year=2011, # Use current date time to generate a date in the future
                          number = self.approved_cards["visa"]["number"],
                          verification_value = self.approved_cards["visa"]["cvd"])
        resp = self.merchant.purchase(8, credit_card)
        self.assertNotEquals(resp["status"], "SUCCESS")

    def testPurchase(self):
        credit_card = self.ccFactory(self.approved_cards["visa"]["number"],
                                     self.approved_cards["visa"]["cvd"])
        response = self.merchant.purchase('1.00', credit_card)
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)

    def testPurchaseVoid(self):
        credit_card = self.ccFactory(self.approved_cards["visa"]["number"],
                                     self.approved_cards["visa"]["cvd"])
        response = self.merchant.purchase('1.00', credit_card)
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)
        response = self.merchant.void({"txnid": txnid, "amount":'1.00'})
        self.assertEquals(response["status"], "SUCCESS")

    def testPurchaseReturn(self):
        credit_card = self.ccFactory(self.approved_cards["visa"]["number"],
                                     self.approved_cards["visa"]["cvd"])
        response = self.merchant.purchase('5.00', credit_card)
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)
        response = self.merchant.credit('4.00', txnid)
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)

    def testAuthorize(self):
        credit_card = self.ccFactory(self.approved_cards["visa"]["number"],
                                     self.approved_cards["visa"]["cvd"])
        response = self.merchant.authorize('1.00', credit_card)
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)

    def testAuthorizeComplete(self):
        ''' Preauth and complete '''
        credit_card = self.ccFactory(self.approved_cards["visa"]["number"],
                                     self.approved_cards["visa"]["cvd"])
        response = self.merchant.authorize('1.00', credit_card)
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)
        response = self.merchant.capture('1.00', txnid)
        self.assertEquals(response["status"], "SUCCESS")

    def testAuthorizeCancel(self):
        ''' Preauth and cancel '''
        credit_card = self.ccFactory(self.approved_cards["visa"]["number"],
                                     self.approved_cards["visa"]["cvd"])
        response = self.merchant.authorize('1.00', credit_card)
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)
        response = self.merchant.unauthorize(None, txnid)
        self.assertEquals(response["status"], "SUCCESS")

    def testCreateProfile(self):
        credit_card = self.ccFactory(self.approved_cards["visa"]["number"],
                                     self.approved_cards["visa"]["cvd"])
        response = self.merchant.store(credit_card, {"billing_address":self.billing_address})
        self.assertEquals(response["status"], "SUCCESS")

        customer_code = response["customer"]
        self.assertIsNotNone(customer_code)

        response = self.merchant.purchase('1.00', None, {"customer_code":customer_code})
        self.assertEquals(response["status"], "SUCCESS")
        txnid = response["txnid"]
        self.assertIsNotNone(txnid)
