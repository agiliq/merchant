from datetime import datetime
from decimal import Decimal
import sha

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
#   Don't support Maestro yet, because it needs 'issueno' to be passed,
#   which isn't supported by Maestro class yet.
    }

GLOBALIRIS_BASE_URL = "https://remote.globaliris.com/RealAuth"

class GlobalIrisGateway(Gateway):

    default_currency = "GBP"
    supported_countries = ["GB"]
    supported_cardtypes = [Visa, MasterCard, AmericanExpress]
    homepage_url = "https://resourcecentre.globaliris.com/"
    display_name = "Global Iris"

    def __init__(self, shared_secret=None, merchant_id=None, sub_account=None):
        if shared_secret is None:
            shared_secret = settings.MERCHANT_SETTINGS['global_iris']['SHARED_SECRET']
        if merchant_id is None:
            merchant_id = settings.MERCHANT_SETTINGS['global_iris']['MERCHANT_ID']
        if sub_account is None:
            sub_account = settings.MERCHANT_SETTINGS['global_iris']['SUB_ACCOUNT']

        self.shared_secret = shared_secret
        self.merchant_id = merchant_id
        self.sub_account = sub_account

    def get_signature(self, data):
        d = data.copy()
        d['merchant_id'] = self.merchant_id
        val1 = "{timestamp}.{merchant_id}.{order_id}.{amount_normalized}.{currency_code}.{card.number}".format(**d)
        hash1 = sha.sha(val1).hexdigest()
        val2 = "{0}.{1}".format(hash1, self.shared_secret)
        hash2 = sha.sha(val2).hexdigest()
        return hash2

    def build_xml(self, data):
        all_data = {
            'currency_code': self.default_currency,
            'merchant_id': self.merchant_id,
            'sub_account': self.sub_account,
            }

        all_data.update(data)
        if not 'timestamp' in all_data:
            all_data['timestamp'] = datetime.now()
        all_data['timestamp'] = all_data['timestamp'].strftime('%Y%m%d%H%M%S')

        currency = all_data['currency_code']
        if currency in ['GBP', 'USD', 'EUR']:
            all_data['amount_normalized'] = int(all_data['amount'] * Decimal('100.00'))
        else:
            raise ValueError("Don't know how to normalise amounts in currency %s" % currency)
        card = all_data['card']
        card.month_normalized = "%02d" % int(card.month)
        year = int(card.year)
        card.year_normalized = "%02d" % (year if year < 100 else int(str(year)[-2:]))
        card.name_normalized = CARD_NAMES[card.__class__]

        # sign
        all_data['sha1_hash'] = self.get_signature(all_data)

        return render_to_string("billing/global_iris_request.xml", all_data).encode('utf-8')

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
        return self.handle_response(self._do_request(xml), "purchase")

    def _failure(self, type, message, response, response_code=None):
        transaction_was_unsuccessful.send(self, type=type, response=response)
        retval = {"status": "FAILURE",
                  "message": message,
                  "response": response,
                  }
        if response_code is not None:
            retval['response_code'] = response_code
        return retval

    def _success(self, type, message, response):
        transaction_was_successful.send(self, type=type, response=response)
        return {"status": "SUCCESS",
                "message": message,
                "response": response,
                }

    def handle_response(self, response, type):
        if response.status_code != 200:
            return self._failure(type, response.reason, response)

        # Parse XML
        xml = lxml.etree.fromstring(response.content)
        response_code = xml.find('result').text
        message = xml.find('message').text
        if response_code == '00':
            return self._success(type, message, response)

        else:
            return self._failure(type, message, response, int(response_code))

    def _do_request(self, xml):
        return requests.post(GLOBALIRIS_BASE_URL, xml)
