# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

import datetime

from suds.client import Client
from suds.cache import ObjectCache
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from billing import Gateway, GatewayNotConfigured
from billing.models import PaylaneTransaction, PaylaneAuthorization
from billing.utils.credit_card import CreditCard, InvalidCard, Visa, MasterCard
from billing.utils.paylane import PaylaneError
from billing.signals import transaction_was_successful, transaction_was_unsuccessful


class PaylaneGateway(Gateway):
    """

    """
    default_currency = "EUR"
    supported_cardtypes = [Visa, MasterCard]
    supported_countries = ['PT']
    homepage_url = 'http://www.paylane.com/'
    display_name = 'Paylane'

    def __init__(self):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("paylane"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        paylane_settings = merchant_settings["paylane"]
        wsdl = paylane_settings.get('WSDL', 'https://direct.paylane.com/wsdl/production/Direct.wsdl')
        wsdl_cache = paylane_settings.get('SUDS_CACHE_DIR', '/tmp/suds')
        username = paylane_settings.get('USERNAME', '')
        password = paylane_settings.get('PASSWORD', '')

        self.client = Client(wsdl, username=username, password=password, cache=ObjectCache(location=wsdl_cache, days=15))

    def _validate(self, card):
        if not isinstance(card, CreditCard):
            raise InvalidCard('credit_card not an instance of CreditCard')

        if not self.validate_card(card):
            raise InvalidCard('Invalid Card')

        card.month = '%02d' % card.month

    def authorize(self, money, credit_card, options=None):
        """Authorization for a future capture transaction"""
        self._validate(credit_card)

        params = self.client.factory.create('ns0:multi_sale_params')
        params['payment_method'] = {}
        params['payment_method']['card_data'] = {}
        params['payment_method']['card_data']['card_number'] = credit_card.number
        params['payment_method']['card_data']['card_code'] = credit_card.verification_value
        params['payment_method']['card_data']['expiration_month'] = credit_card.month
        params['payment_method']['card_data']['expiration_year'] = credit_card.year
        params['payment_method']['card_data']['name_on_card'] = '%s %s' % (credit_card.first_name, credit_card.last_name)
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

        status = None
        response = None
        transaction.success = hasattr(res, 'OK')
        transaction.save()

        if hasattr(res, 'OK'):
            status = 'SUCCESS'
            authz = PaylaneAuthorization()
            authz.sale_authorization_id = res.OK.id_sale_authorization
            authz.transaction = transaction
            authz.first_authorization = True
            authz.save()

            response = {'transaction': transaction, 'authorization': authz}
            transaction_was_successful.send(sender=self, type='recurring', response=response)

        else:
            status = 'FAILURE'
            response = {'error': PaylaneError(getattr(res.ERROR, 'error_number'),
                                    getattr(res.ERROR, 'error_description'),
                                    getattr(res.ERROR, 'processor_error_number', ''),
                                    getattr(res.ERROR, 'processor_error_description', '')),
                        'transaction': transaction
                        }
            transaction_was_unsuccessful.send(sender=self, type='recurring', response=response)

        return {'status': status, 'response': response}

    def capture(self, money, authorization, options=None):
        """Capture all funds from a previously authorized transaction"""
        product = options['product']
        res = self.client.service.captureSale(id_sale_authorization=authorization.sale_authorization_id,
                    amount=money,
                    description=product)

        previous_transaction = authorization.transaction

        transaction = PaylaneTransaction()
        transaction.amount = previous_transaction.amount
        transaction.customer_name = previous_transaction.customer_name
        transaction.customer_email = previous_transaction.customer_email
        transaction.product = previous_transaction.product

        status = None
        response = None
        transaction.success = hasattr(res, 'OK')
        transaction.save()
        if hasattr(res, 'OK'):
            status = 'SUCCESS'
            authz = PaylaneAuthorization()
            authz.sale_authorization_id = authorization.sale_authorization_id
            authz.transaction = transaction
            authz.save()
            response = {'transaction': transaction, 'authorization': authz}
            transaction_was_successful.send(sender=self, type='bill_recurring', response=response)
        else:
            status = 'FAILURE'
            response = {'error': PaylaneError(getattr(res.ERROR, 'error_number'),
                                    getattr(res.ERROR, 'error_description'),
                                    getattr(res.ERROR, 'processor_error_number', ''),
                                    getattr(res.ERROR, 'processor_error_description', '')),
                        'transaction': transaction
                        }
            transaction_was_unsuccessful.send(sender=self, type='bill_recurring', response=response)

        return {'status': status, 'response': response}

    def purchase(self, money, credit_card, options=None):
        """One go authorize and capture transaction"""
        self._validate(credit_card)

        params = self.client.factory.create('ns0:multi_sale_params')
        params['payment_method'] = {}
        params['payment_method']['card_data'] = {}
        params['payment_method']['card_data']['card_number'] = credit_card.number
        params['payment_method']['card_data']['card_code'] = credit_card.verification_value
        params['payment_method']['card_data']['expiration_month'] = credit_card.month
        params['payment_method']['card_data']['expiration_year'] = credit_card.year
        params['payment_method']['card_data']['name_on_card'] = '%s %s' % (credit_card.first_name, credit_card.last_name)
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
        params['product']['description'] = product

        res = self.client.service.multiSale(params)

        transaction = PaylaneTransaction()
        transaction.amount = money
        transaction.customer_name = customer.name
        transaction.customer_email = customer.email
        transaction.product = product

        status = None
        response = None
        transaction.success = hasattr(res, 'OK')
        transaction.save()

        if hasattr(res, 'OK'):
            status = 'SUCCESS'
            response = {'transaction': transaction}
            transaction_was_successful.send(sender=self, type='purchase', response=response)
        else:
            status = 'FAILURE'
            response = {'error': PaylaneError(getattr(res.ERROR, 'error_number'),
                                    getattr(res.ERROR, 'error_description'),
                                    getattr(res.ERROR, 'processor_error_number', ''),
                                    getattr(res.ERROR, 'processor_error_description', '')),
                        'transaction': transaction
                        }
            transaction_was_unsuccessful.send(sender=self, type='purchase', response=response)

        return {'status': status, 'response': response}

    def recurring(self, money, credit_card, options=None):
        """Setup a recurring transaction"""
        return self.authorize(money, credit_card, options)

    def void(self, identification, options=None):
        """Null/Blank/Delete a previous transaction"""
        res = self.client.service.closeSaleAuthorization(id_sale_authorization=identification)
        if hasattr(res, 'OK'):
            return {'status': 'SUCCESS'}
        else:
            return {'status': 'FAILURE',
                    'response': {'error': PaylaneError(getattr(res.ERROR, 'error_number'),
                                            getattr(res.ERROR, 'error_description'),
                                            getattr(res.ERROR, 'processor_error_number', ''),
                                            getattr(res.ERROR, 'processor_error_description', '')),
                                }
                    }

    def bill_recurring(self, amount, authorization, description):
        """ Debit a recurring transaction payment, eg. monthly subscription.

            Use the result of recurring() as the paylane_recurring parameter.
            If this transaction is successful, use it's response as input for the
            next bill_recurring() call.
        """
        processing_date = datetime.datetime.today().strftime("%Y-%m-%d")
        res = self.client.service.resale(id_sale=authorization.sale_authorization_id, amount=amount, currency=self.default_currency,
                                        description=description, processing_date=processing_date, resale_by_authorization=authorization)

        previous_transaction = authorization.transaction

        transaction = PaylaneTransaction()
        transaction.amount = previous_transaction.amount
        transaction.customer_name = previous_transaction.customer_name
        transaction.customer_email = previous_transaction.customer_email
        transaction.product = previous_transaction.product

        status = None
        response = None
        transaction.success = hasattr(res, 'OK')
        transaction.save()
        if hasattr(res, 'OK'):
            status = 'SUCCESS'
            authz = PaylaneAuthorization()
            authz.sale_authorization_id = authorization.sale_authorization_id
            authz.transaction = transaction
            authz.save()
            response = {'transaction': transaction, 'authorization': authz}
            transaction_was_successful.send(sender=self, type='bill_recurring', response=response)
        else:
            status = 'FAILURE'
            response = {'error': PaylaneError(getattr(res.ERROR, 'error_number'),
                                    getattr(res.ERROR, 'error_description'),
                                    getattr(res.ERROR, 'processor_error_number', ''),
                                    getattr(res.ERROR, 'processor_error_description', '')),
                        'transaction': transaction
                        }
            transaction_was_unsuccessful.send(sender=self, type='bill_recurring', response=response)

        return {'status': status, 'response': response}
