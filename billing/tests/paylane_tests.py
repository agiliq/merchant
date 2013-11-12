# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa, CreditCard
from billing import get_gateway
from billing.signals import *
from billing.utils.paylane import *
from billing.models import PaylaneTransaction, PaylaneAuthorization

#This is needed because Paylane doesn't like too many requests in a very short time


THROTTLE_CONTROL_SECONDS = 60

# VISA test card numbers
# 4929966723331981 #
# 4916437826836305 #
# 4532830407731057
# 4539824967650347
# 4278255665174428
# 4556096020428973
# 4929242798450290
# 4024007124529719
# 4024007172509597
# 4556969412054203


@skipIf(not settings.MERCHANT_SETTINGS.get("paylane", None), "gateway not configured")
class PaylaneTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("paylane")
        self.merchant.test_mode = True
        address = PaylanePaymentCustomerAddress()
        address.street_house = 'Av. 24 de Julho, 1117'
        address.city = 'Lisbon'
        address.zip_code = '1700-000'
        address.country_code = 'PT'
        self.customer = PaylanePaymentCustomer(name='Celso Pinto', email='celso@modelo3.pt', ip_address='8.8.8.8', address=address)
        self.product = PaylanePaymentProduct(description='Paylane test payment')

    def tearDown(self):
        for authz in PaylaneAuthorization.objects.all():
            self.merchant.void(authz.sale_authorization_id)

    def testOneShotPurchaseOK(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4012888888881881', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = {}
        res = self.merchant.purchase(1.0, credit_card, options=options)
        self.assertEqual(res['status'], 'SUCCESS', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertFalse('authorization' in res['response'])

    def testOneShotPurchaseError(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4929966723331981', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = {}
        res = self.merchant.purchase(float(PaylaneError.ERR_CARD_EXPIRED), credit_card, options=options)
        self.assertEqual(res['status'], 'FAILURE', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertFalse('authorization' in res['response'])
        self.assertTrue('error' in res['response'])
        self.assertEqual(res['response']['error'].error_code, PaylaneError.ERR_CARD_EXPIRED)

    def testRecurringSetupOK(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4242424242424242', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.recurring(1.0, credit_card, options=options)
        self.assertEqual(res['status'], 'SUCCESS', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)

    def testRecurringSetupError(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4916437826836305', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.recurring(float(PaylaneError.ERR_CARD_EXPIRED), credit_card, options=options)
        self.assertEqual(res['status'], 'FAILURE', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertFalse('authorization' in res['response'])
        self.assertTrue('error' in res['response'])
        self.assertEqual(res['response']['error'].error_code, PaylaneError.ERR_CARD_EXPIRED)

    def testRecurringBillingOK(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4000111111111115', verification_value="100")
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.recurring(1.0, credit_card, options=options)
        self.assertEqual(res['status'], 'SUCCESS', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)

        bill1 = self.merchant.bill_recurring(12.0, res['response']['authorization'], 'OK recurring')
        self.assertEqual(bill1['status'], 'SUCCESS', unicode(bill1['response']))
        self.assertTrue('transaction' in bill1['response'])
        self.assertTrue('authorization' in bill1['response'])

    def testRecurringBillingFailWithChargeback(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4111111111111111', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.recurring(1.0, credit_card, options=options)
        self.assertEqual(res['status'], 'SUCCESS', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)

        bill1 = self.merchant.bill_recurring(12.0, res['response']['authorization'], 'OK recurring')
        self.assertEqual(bill1['status'], 'SUCCESS', unicode(bill1['response']))
        self.assertTrue('transaction' in bill1['response'])
        self.assertTrue('authorization' in bill1['response'])

        bill2 = self.merchant.bill_recurring(float(PaylaneError.ERR_RESALE_WITH_CHARGEBACK), bill1['response']['authorization'], 'Fail recurring')
        self.assertEqual(bill2['status'], 'FAILURE', unicode(bill2['response']))
        self.assertTrue('transaction' in bill2['response'])
        self.assertTrue('error' in bill2['response'])
        self.assertEqual(bill2['response']['error'].error_code, PaylaneError.ERR_RESALE_WITH_CHARGEBACK)

    def testAuthorizeOK(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4532830407731057', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.authorize(1.0, credit_card, options=options)
        self.assertEqual(res['status'], 'SUCCESS', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)

    def testAuthorizeError(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4539824967650347', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.authorize(float(PaylaneError.ERR_CARD_EXPIRED), credit_card, options=options)
        self.assertEqual(res['status'], 'FAILURE', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertFalse('authorization' in res['response'])
        self.assertTrue('error' in res['response'])
        self.assertEqual(res['response']['error'].error_code, PaylaneError.ERR_CARD_EXPIRED)

    def testCaptureOK(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4278255665174428', verification_value="100")
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.authorize(36.0, credit_card, options=options)
        self.assertEqual(res['status'], 'SUCCESS', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)

        bill1 = self.merchant.capture(36.0, res['response']['authorization'], options)
        self.assertEqual(bill1['status'], 'SUCCESS', unicode(bill1['response']))
        self.assertTrue('transaction' in bill1['response'])
        self.assertTrue('authorization' in bill1['response'])

    def testCaptureError(self):
        credit_card = Visa(first_name='Celso', last_name='Pinto', month=10, year=2020, number='4556096020428973', verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.authorize(1.0, credit_card, options=options)
        self.assertEqual(res['status'], 'SUCCESS', unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)

        bill2 = self.merchant.capture(float(PaylaneError.ERR_RESALE_WITH_CHARGEBACK), res['response']['authorization'], options)
        self.assertEqual(bill2['status'], 'FAILURE', unicode(bill2['response']))
        self.assertTrue('transaction' in bill2['response'])
        self.assertTrue('error' in bill2['response'])
        self.assertEqual(bill2['response']['error'].error_code, 443)
