# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

import datetime

from suds.client import Client
from suds.cache import ObjectCache
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from billing import Gateway
from billing.models import PaylaneResponse
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

        if hasattr(res,'OK'):
            return {'status':'SUCCESS','response':PaylaneResponse(sale_authorization_id=res.OK.id_sale)}
        else:
            return {'status':'FAILURE',
                    'response':PaylaneError(getattr(res.ERROR,'error_number'),
                                            getattr(res.ERROR,'error_description'),
                                            getattr(res.ERROR,'processor_error_number',''),
                                            getattr(res.ERROR,'processor_error_description',''))
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

        if hasattr(res,'OK'):
            return {'status':'SUCCESS','response':PaylaneResponse(sale_authorization_id=res.OK.id_sale_authorization)}
        else:
            return {'status':'FAILURE',
                    'response':PaylaneError(getattr(res.ERROR,'error_number'),
                                            getattr(res.ERROR,'error_description'),
                                            getattr(res.ERROR,'processor_error_number',''),
                                            getattr(res.ERROR,'processor_error_description',''))
                    }

    def bill_recurring(self,amount,paylane_response,description):
        """ Debit a recurring transaction payment, eg. monthly subscription.
        
            Use the result of recurring() as the paylane_response parameter.
            If this transaction is successful, use it's response as input for the
            next bill_recurring() call.
        """
        processing_date = datetime.datetime.today().strftime("%Y-%m-%d")
        res = self.client.service.resale(id_sale=paylane_response.sale_authorization_id,amount=amount,currency=self.default_currency,
                                        description=description,processing_date=processing_date)
        
        if hasattr(res,'OK'):
            return {'status':'SUCCESS','response':PaylaneResponse(sale_authorization_id=res.OK.id_sale)}
        else:
            return {'status':'FAILURE',
                    'response':PaylaneError(getattr(res.ERROR,'error_number'),
                                            getattr(res.ERROR,'error_description'),
                                            getattr(res.ERROR,'processor_error_number',''),
                                            getattr(res.ERROR,'processor_error_description',''))
                    }
