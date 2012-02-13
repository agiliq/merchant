# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

import time

from django.test import TestCase
from billing.gateway import CardNotSupported
from billing.utils.credit_card import Visa,CreditCard
from billing import get_gateway
from billing.signals import *

from billing.utils.paylane import *
from billing.models import PaylaneTransaction,PaylaneAuthorization

#This is needed because Paylane doesn't like too many requests in a very short time
THROTTLE_CONTROL_SECONDS = 60

class PaylaneTestCase(TestCase):
    def setUp(self):
        self.merchant = get_gateway("paylane")
        self.merchant.test_mode = True
        address = PaylanePaymentCustomerAddress()
        address.street_house = 'Av. 24 de Julho, 1117'
        address.city = 'Lisbon'
        address.zip_code = '1700-000'
        address.country_code = 'PT'
        self.customer = PaylanePaymentCustomer(name='Celso Pinto',email='celso@modelo3.pt',ip_address='8.8.8.8',address=address)
        self.product = PaylanePaymentProduct(description='Paylane test payment')
        
    def tearDown(self):
        for authz in PaylaneAuthorization.objects.all():
            self.merchant.void(authz.sale_authorization_id)
        
    def testOneShotPurchaseOK(self):
        credit_card = Visa(first_name='Celso',last_name='Pinto',month=10,year=2012,number='4012888888881881',verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.purchase(1.0,credit_card,options=options)
        self.assertEqual(res['status'],'SUCCESS',unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertFalse('authorization' in res['response'])
        
    def testRecurringSetupOK(self):
        credit_card = Visa(first_name='Celso',last_name='Pinto',month=10,year=2012,number='4242424242424242',verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.recurring(1.0,credit_card,options=options)
        self.assertEqual(res['status'],'SUCCESS',unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)
        
    def testRecurringBillingOK(self):
        credit_card = Visa(first_name='Celso',last_name='Pinto',month=10,year=2012,number='4000111111111115',verification_value="100")
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.recurring(1.0,credit_card,options=options)
        self.assertEqual(res['status'],'SUCCESS',unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)
                
        time.sleep(THROTTLE_CONTROL_SECONDS)
        bill1 = self.merchant.bill_recurring(12.0,res['response']['authorization'],'OK recurring')
        self.assertEqual(bill1['status'],'SUCCESS',unicode(bill1['response']))
        self.assertTrue('transaction' in bill1['response'])
        self.assertTrue('authorization' in bill1['response'])

        time.sleep(THROTTLE_CONTROL_SECONDS)
        bill2 = self.merchant.bill_recurring(12.0,bill1['response']['authorization'],'OK recurring')
        self.assertEqual(bill2['status'],'SUCCESS',unicode(bill2['response']))
        self.assertTrue('transaction' in bill2['response'])
        self.assertTrue('authorization' in bill2['response'])

    def testRecurringBillingFailWithChargeback(self):
        credit_card = Visa(first_name='Celso',last_name='Pinto',month=10,year=2012,number='4111111111111111',verification_value=435)
        options = {}
        options['customer'] = self.customer
        options['product'] = self.product
        res = self.merchant.recurring(1.0,credit_card,options=options)
        self.assertEqual(res['status'],'SUCCESS',unicode(res['response']))
        self.assertTrue('transaction' in res['response'])
        self.assertTrue('authorization' in res['response'])
        self.assertTrue(res['response']['authorization'].sale_authorization_id > 0)

        time.sleep(THROTTLE_CONTROL_SECONDS)
        bill1 = self.merchant.bill_recurring(12.0,res['response']['authorization'],'OK recurring')
        self.assertEqual(bill1['status'],'SUCCESS',unicode(bill1['response']))
        self.assertTrue('transaction' in bill1['response'])
        self.assertTrue('authorization' in bill1['response'])

        time.sleep(THROTTLE_CONTROL_SECONDS)
        bill2 = self.merchant.bill_recurring(float(PaylaneError.ERR_RESALE_WITH_CHARGEBACK),bill1['response']['authorization'],'Fail recurring')
        self.assertEqual(bill2['status'],'FAILURE',unicode(bill2['response']))
        self.assertTrue('transaction' in bill2['response'])
        self.assertTrue('error' in bill2['response'])
        self.assertEqual(bill2['response']['error'].error_code,PaylaneError.ERR_RESALE_WITH_CHARGEBACK)
