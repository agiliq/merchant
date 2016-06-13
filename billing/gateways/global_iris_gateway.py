from datetime import datetime
from decimal import Decimal
from hashlib import sha1
import string

from django.conf import settings
from django.template.loader import render_to_string
import lxml
import requests

from billing import Gateway
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import Visa, MasterCard, AmericanExpress, InvalidCard


# See https://resourcecentre.globaliris.com/documents/pdf.html?id=43 for details

CARD_NAMES = {
    Visa: 'VISA',
    MasterCard: 'MC',
    AmericanExpress: 'AMEX',
    # Maestro and Switch are probably broken due to need for issue number to be passed.
    }


class Config(object):
    def __init__(self, config_dict):
        self.shared_secret = config_dict['SHARED_SECRET']
        self.merchant_id = config_dict['MERCHANT_ID']
        self.account = config_dict['ACCOUNT']


class GlobalIrisBase(object):

    default_currency = "GBP"
    supported_countries = ["GB"]
    supported_cardtypes = [Visa, MasterCard, AmericanExpress]
    homepage_url = "https://resourcecentre.globaliris.com/"

    def __init__(self, config=None, test_mode=None):
        if config is None:
            config = settings.MERCHANT_SETTINGS['global_iris']
        self.config = config

        if test_mode is None:
            test_mode = getattr(settings, 'MERCHANT_TEST_MODE', True)
        self.test_mode = test_mode

    def get_config(self, credit_card):
        setting_name_base = 'LIVE' if not self.test_mode else 'TEST'
        setting_names = ['%s_%s' % (setting_name_base, CARD_NAMES[credit_card.card_type]),
                         setting_name_base]

        for name in setting_names:
            try:
                config_dict = self.config[name]
            except KeyError:
                continue
            return Config(config_dict)

        raise KeyError("Couldn't find key %s in config %s" % (' or '.join(setting_names), self.config))

    def make_timestamp(self, dt):
        return dt.strftime('%Y%m%d%H%M%S')

    def standardize_data(self, data):
        config = self.get_config(data['card'])
        all_data = {
            'currency': self.default_currency,
            'merchant_id': config.merchant_id,
            'account': config.account,
            }

        all_data.update(data)
        if not 'timestamp' in all_data:
            all_data['timestamp'] = datetime.now()
        all_data['timestamp'] = self.make_timestamp(all_data['timestamp'])
        currency = all_data['currency']
        if currency in ['GBP', 'USD', 'EUR', 'AUD']:
            all_data['amount_normalized'] = int(all_data['amount'] * Decimal('100.00'))
        else:
            raise ValueError("Don't know how to normalise amounts in currency %s" % currency)
        card = all_data['card']
        card.month_normalized = "%02d" % int(card.month)
        year = int(card.year)
        card.year_normalized = "%02d" % (year if year < 100 else int(str(year)[-2:]))
        card.name_normalized = CARD_NAMES[card.card_type]

        def fix_address(address_dict):
            if 'post_code' in address_dict and 'street_address' in address_dict:
                address_dict['code'] = self.address_to_code(address_dict['street_address'],
                                                            address_dict['post_code'])

        if 'billing_address' in data:
            fix_address(data['billing_address'])
        if 'shipping_address' in data:
            fix_address(data['shipping_address'])

        all_data['sha1_hash'] = self.get_standard_signature(all_data, config)
        return all_data

    def address_to_code(self, street_address, post_code):
        """
        Returns a post 'code' in format required by RealAuth, from
        the street address and the post code.
        """
        # See https://resourcecentre.globaliris.com/documents/pdf.html?id=102, p27
        get_digits = lambda s: ''.join(c for c in s if c in string.digits)
        return "{0}|{1}".format(get_digits(post_code),
                                get_digits(street_address),
                                )

    def get_signature(self, data, config, signing_string):
        d = data.copy()
        d['merchant_id'] = config.merchant_id
        val1 = signing_string.format(**d)
        hash1 = sha1(val1).hexdigest()
        val2 = "{0}.{1}".format(hash1, config.shared_secret)
        hash2 = sha1(val2).hexdigest()
        return hash2

    def get_standard_signature(self, data, config):
        return self.get_signature(data, config, "{timestamp}.{merchant_id}.{order_id}.{amount_normalized}.{currency}.{card.number}")

    def do_request(self, xml):
        return requests.post(self.base_url, xml)


class GlobalIrisGateway(GlobalIrisBase, Gateway):

    display_name = "Global Iris"

    base_url = "https://remote.globaliris.com/RealAuth"

    def build_xml(self, data):
        all_data = self.standardize_data(data)
        return render_to_string("billing/global_iris_realauth_request.xml", all_data).encode('utf-8')

    def purchase(self, money, credit_card, options=None):
        if options is None or 'order_id' not in options:
            raise ValueError("Required parameter 'order_id' not found in options")

        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        data = {
            'amount': money,
            'card': credit_card,
            }
        data.update(options)
        xml = self.build_xml(data)
        return self.handle_response(self.do_request(xml), "purchase")

    def _failure(self, type, message, response, response_code=None):
        transaction_was_unsuccessful.send(self, type=type, response=response, response_code=response_code)
        retval = {"status": "FAILURE",
                  "message": message,
                  "response": response,
                  }
        if response_code is not None:
            retval['response_code'] = response_code
        return retval

    def _success(self, type, message, response, response_code=None, **kwargs):
        transaction_was_successful.send(self, type=type, response=response, response_code=response_code)
        retval = {"status": "SUCCESS",
                  "message": message,
                  "response": response,
                  "response_code": response_code,
                  }
        retval.update(kwargs)
        return retval

    def handle_response(self, response, type):
        if response.status_code != 200:
            return self._failure(type, response.reason, response)

        # Parse XML
        xml = lxml.etree.fromstring(response.content)
        response_code = xml.find('result').text
        message = xml.find('message').text
        if response_code == '00':
            kwargs = {}
            merge_xml_to_dict(xml, kwargs, ['avsaddressresponse', 'avspostcoderesponse', 'cvnresult'])
            cardissuer = xml.find('cardissuer')
            if cardissuer is not None:
                cardissuer_data = {}
                merge_xml_to_dict(cardissuer, cardissuer_data, ['bank', 'country', 'countrycode', 'region'])
                kwargs['cardissuer'] = cardissuer_data

            return self._success(type, message, response, response_code=response_code, **kwargs)

        else:
            return self._failure(type, message, response, response_code=response_code)


def merge_xml_to_dict(node, d, attrs):
    for n in attrs:
        elem = node.find(n)
        if elem is not None:
            d[n] = elem.text
