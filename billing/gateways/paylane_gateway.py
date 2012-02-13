# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

import datetime

from suds.client import Client
from suds.cache import ObjectCache
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from billing import Gateway
from billing.models import PaylaneTransaction,PaylaneAuthorization
from billing.utils.credit_card import CreditCard,InvalidCard,Visa,MasterCard
from billing.utils.paylane import PaylaneError
from billing.signals import transaction_was_successful,transaction_was_unsuccessful

class PaylaneGateway(Gateway):
    """
        
    """
    default_currency = "EUR"
    supported_cardtypes = [Visa,MasterCard]
    supported_countries = ['PT',]
    homepage_url = 'http://www.paylane.com/'
    display_name = 'Paylane'
    
    def __init__(self):
        wsdl = getattr(settings,'PAYLANE_WSDL','https://direct.paylane.com/wsdl/production/Direct.wsdl')
        wsdl_cache = getattr(settings,'SUDS_CACHE_DIR','/tmp/suds')
        if self.test_mode:
            username = getattr(settings, 'PAYLANE_USERNAME_TEST', '')
            password = getattr(settings, 'PAYLANE_PASSWORD_TEST', '')
        else:
            username = settings.PAYLANE_USERNAME
            password = settings.PAYLANE_PASSWORD
            
        self.client = Client(wsdl, username=username, password=password,cache = ObjectCache(location=wsdl_cache,days=15))

    def _validate(self,card):
        if not isinstance(card,CreditCard):
            raise InvalidCard('credit_card not an instance of CreditCard')
        if not self.validate_card(card):
            raise InvalidCard('Invalid Card')

    def purchase(self,money,credit_card,options=None):
        """One go authorize and capture transaction"""
        self._validate(credit_card)

        params = self.client.factory.create('ns0:multi_sale_params')
        params['payment_method'] = {}
        params['payment_method']['card_data'] = {}
        params['payment_method']['card_data']['card_number'] = credit_card.number
        params['payment_method']['card_data']['card_code'] = credit_card.verification_value
        params['payment_method']['card_data']['expiration_month'] = credit_card.month
        params['payment_method']['card_data']['expiration_year'] = credit_card.year
        params['payment_method']['card_data']['name_on_card'] = '%s %s' % (credit_card.first_name,credit_card.last_name)
        params['capture_later'] = False
        
        customer = options['customer']
        params['customer']['name'] = customer.name
        params['customer']['email'] = customer.email
        params['customer']['ip'] = customer.ip_address
        params['customer']['address']['street_house'] = customer.address.street_house
        params['customer']['address']['city'] = customer.address.city
        if customer.address.state:
            params['customer']['address']['state'] = customer.address.state
        params['customer']['address']['zip'] = customer.address.zip_code
        params['customer']['address']['country_code'] = customer.address.country_code
        
        params['amount'] = money
        params['currency_code'] = self.default_currency
        
        product = options['product']
        params['product'] = {}
        params['product']['description'] = product.description

        res = self.client.service.multiSale(params)

        transaction = PaylaneTransaction()
        transaction.amount = money
        transaction.customer_name = customer.name
        transaction.customer_email = customer.email
        transaction.product = product.description
        
        if hasattr(res,'OK'):
            transaction.success = True
            transaction.save()
            
            return {'status':'SUCCESS','response':{'transaction':transaction}}
        else:
            transaction.success = False
            error_code = int(getattr(res.ERROR,'error_number'))
            error_description = getattr(res.ERROR,'error_description')
            acquirer_error = getattr(res.ERROR,'processor_error_number','')
            acquirer_description = getattr(res.ERROR,'processor_error_description','')
            transaction.save()
            
            return {'status':'FAILURE',
                    'response':{'error':PaylaneError(getattr(res.ERROR,'error_number'),
                                            getattr(res.ERROR,'error_description'),
                                            getattr(res.ERROR,'processor_error_number',''),
                                            getattr(res.ERROR,'processor_error_description','')),
                                'transaction':transaction
                                }
                    }

    def recurring(self,money,credit_card,options=None):
        """Setup a recurring transaction"""
        self._validate(credit_card)

        params = self.client.factory.create('ns0:multi_sale_params')
        params['payment_method'] = {}
        params['payment_method']['card_data'] = {}
        params['payment_method']['card_data']['card_number'] = credit_card.number
        params['payment_method']['card_data']['card_code'] = credit_card.verification_value
        params['payment_method']['card_data']['expiration_month'] = credit_card.month
        params['payment_method']['card_data']['expiration_year'] = credit_card.year
        params['payment_method']['card_data']['name_on_card'] = '%s %s' % (credit_card.first_name,credit_card.last_name)
        params['capture_later'] = True
        
        customer = options['customer']
        params['customer']['name'] = customer.name
        params['customer']['email'] = customer.email
        params['customer']['ip'] = customer.ip_address
        params['customer']['address']['street_house'] = customer.address.street_house
        params['customer']['address']['city'] = customer.address.city
        if customer.address.state:
            params['customer']['address']['state'] = customer.address.state
        params['customer']['address']['zip'] = customer.address.zip_code
        params['customer']['address']['country_code'] = customer.address.country_code
        
        params['amount'] = money
        params['currency_code'] = self.default_currency
        
        product = options['product']
        params['product'] = {}
        params['product']['description'] = product.description

        res = self.client.service.multiSale(params)

        transaction = PaylaneTransaction()
        transaction.amount = money
        transaction.customer_name = customer.name
        transaction.customer_email = customer.email
        transaction.product = product.description
        
        if hasattr(res,'OK'):
            transaction.success = True
            transaction.save()
            
            authz = PaylaneAuthorization.objects.create(sale_authorization_id=res.OK.id_sale_authorization,transaction=transaction)
            return {'status':'SUCCESS','response':{'transaction':transaction,'authorization':authz}}
        else:
            transaction.success = False
            error_code = int(getattr(res.ERROR,'error_number'))
            error_description = getattr(res.ERROR,'error_description')
            acquirer_error = getattr(res.ERROR,'processor_error_number','')
            acquirer_description = getattr(res.ERROR,'processor_error_description','')
            transaction.save()
            
            return {'status':'FAILURE',
                    'response':{'error':PaylaneError(getattr(res.ERROR,'error_number'),
                                            getattr(res.ERROR,'error_description'),
                                            getattr(res.ERROR,'processor_error_number',''),
                                            getattr(res.ERROR,'processor_error_description','')),
                                'transaction':transaction
                                }
                    }

    def bill_recurring(self,amount,paylane_recurring,description):
        """ Debit a recurring transaction payment, eg. monthly subscription.
        
            Use the result of recurring() as the paylane_recurring parameter.
            If this transaction is successful, use it's response as input for the
            next bill_recurring() call.
        """
        processing_date = datetime.datetime.today().strftime("%Y-%m-%d")
        res = self.client.service.resale(id_sale=paylane_recurring.sale_authorization_id,amount=amount,currency=self.default_currency,
                                        description=description,processing_date=processing_date)
        
        previous_transaction = paylane_recurring.transaction
        
        transaction = PaylaneTransaction()
        transaction.amount = previous_transaction.amount
        transaction.customer_name = previous_transaction.name
        transaction.customer_email = previous_transaction.email
        transaction.product = previous_transaction.description

        if hasattr(res,'OK'):
            transaction.success = True
            transaction.save()
            
            authz = PaylaneAuthorization.objects.create(sale_authorization_id=res.OK.id_sale_authorization,transaction=transaction)            
            return {'status':'SUCCESS','response':{'transaction':transaction,'authorization':authz}}
        else:
            transaction.success = False
            error_code = int(getattr(res.ERROR,'error_number'))
            error_description = getattr(res.ERROR,'error_description')
            acquirer_error = getattr(res.ERROR,'processor_error_number','')
            acquirer_description = getattr(res.ERROR,'processor_error_description','')
            transaction.save()
            
            return {'status':'FAILURE',                    
                    'response':{'error':PaylaneError(getattr(res.ERROR,'error_number'),
                                            getattr(res.ERROR,'error_description'),
                                            getattr(res.ERROR,'processor_error_number',''),
                                            getattr(res.ERROR,'processor_error_description','')),
                                'transaction':transaction
                                }
                    }
