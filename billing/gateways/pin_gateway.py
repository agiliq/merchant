try:
    import json
except ImportError:
    from django.utils import simplejson as json

import pprint
import requests
from copy import copy
from django.conf import settings
from billing import CreditCard
from billing import Gateway, GatewayNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import Visa, MasterCard, DinersClub, JCB, AmericanExpress, InvalidCard
from billing.models.pin_models import *

SSIG = {
    True:  ('SUCCESS', transaction_was_successful),
    False: ('FAILURE', transaction_was_unsuccessful),
}

class PinGateway(Gateway):
    default_currency = "AUD"
    supported_countries = ["AU"]
    supported_cardtypes = [Visa, MasterCard]
    homepage_url = "https://pin.net.au/"
    display_name = "Pin Payments"
    version = '1'
    endpoints = {
        'LIVE': 'api.pin.net.au',
        'TEST': 'test-api.pin.net.au',
    }

    def __init__(self):
        try:
            self.test_mode = settings.MERCHANT_TEST_MODE
            mode = 'TEST' if self.test_mode else 'LIVE'
            self.secret_key = settings.MERCHANT_SETTINGS["pin"][mode]['SECRET']
            self.endpoint = self.endpoints[mode]
        except (AttributeError, KeyError):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)

    def _pin_request(self, method, url, data):
        request_method = getattr(requests, method)
        uri = "https://%s/%s%s" % (self.endpoint, self.version, url)
        auth = (self.secret_key, '')
        headers = {'content-type': 'application/json'}
        if settings.DEBUG:
            # pprint.pprint(auth)
            # pprint.pprint(headers)
            pprint.pprint(data)
        resp = request_method(uri, data=json.dumps(data), auth=auth, headers=headers)
        return resp.status_code == 201, resp.json()

    def _pin_response(self, success, resp, signal_type, obj=None):
        status, signal = SSIG[success]
        signal.send(sender=self, type=signal_type, response=resp)
        return {'status': status, 'response': resp, 'obj': obj}

    def _pin_base(self, money, options):
        return {
            'amount': str(int(money*100)),
            'email': options.get('email', ''),
            'description': options.get('description', ''),
            'currency': options.get('currency', self.default_currency),
            'ip_address': options.get('ip', ''),
        }

    def _pin_card(self, credit_card, options=None):
        address = options['billing_address']
        return {
            "number": credit_card.number,
            "expiry_month": "%02d" % credit_card.month,
            "expiry_year": str(credit_card.year),
            "cvc": credit_card.verification_value,
            "name": '%s %s' % (credit_card.first_name, credit_card.last_name),
            "address_line1": address['address1'],
            "address_line2": address.get('address2', ''),
            "address_city": address['city'],
            "address_postcode": address['zip'],
            "address_state": address['state'],
            "address_country": address['country'],
        }

    def purchase(self, money, credit_card, options=None, commit=True):
        "Charge (without token)"
        data = self._pin_base(money, options)
        data['card'] = self._pin_card(credit_card, options)
        success, resp = self._pin_request('post', '/charges', data)
        charge = None
        if success and commit:
            response = copy(resp['response'])
            del response['card']['name']
            card = PinCard(**response['card'])
            card.first_name = credit_card.first_name
            card.last_name = credit_card.last_name
            card.save()
            charge = PinCharge(card=card)
            for key, value in response.items():
                if key != 'card':
                    setattr(charge, key, value)
            charge.error_message = charge.error_message or ''
            charge.save()
        return self._pin_response(success, resp, 'purchase', charge)

    def authorize(self, money, credit_card, options=None, commit=True):
        "Card tokens"
        data = self._pin_card(credit_card, options)
        success, resp = self._pin_request('post', '/cards', data)
        card = None
        if success and commit:
            response = copy(resp['response'])
            del response['name']
            card = PinCard(**response)
            card.first_name = credit_card.first_name
            card.last_name = credit_card.last_name
            card.save()
        return self._pin_response(success, resp, 'authorize', obj=card)

    def capture(self, money, authorization, options=None, commit=True):
        "Charge (with card/customer token)"
        # authorization is a card/customer token from authorize/store
        data = self._pin_base(money, options)
        card = None
        customer = None
        if authorization.startswith('cus_'):
            data['customer_token'] = authorization
            try:
                customer = PinCustomer.objects.get(token=authorization)
            except PinCustomer.DoesNotExist:
                pass
        elif authorization.startswith('card_'):
            data['card_token'] = authorization
            try:
                card = PinCard.objects.get(token=authorization)
            except PinCard.DoesNotExist:
                pass
        success, resp = self._pin_request('post', '/charges', data)
        charge = None
        if success and commit:
            charge = PinCharge(card=card, customer=customer)
            for key, value in resp['response'].items():
                if key != 'card':
                    setattr(charge, key, value)
            charge.error_message = charge.error_message or ''
            charge.save()
        return self._pin_response(success, resp, 'capture')

    def void(self, identification, options=None):
        raise NotImplementedError

    def credit(self, money, identification, options=None):
        "Refunds"
        url = '/%s/refunds' % identification
        success, resp = self._pin_request('post', url, {})
        # TODO: save model
        return self._pin_response(success, resp, 'credit')

    def recurring(self, money, credit_card, options=None):
        raise NotImplementedError

    def store(self, credit_card, options=None):
        "Customers"
        data = {
            'email': options['email'],
            'card': self._pin_card(credit_card, options),
        }
        if "token" in options:
            url = '/%s/customers' % options['token']
        else:
            url = '/customers'
        success, resp = self._pin_request('post', url, data)
        # TODO: save model
        return self._pin_response(success, resp, 'store')

    def unstore(self, identification, options=None):
        raise NotImplementedError
