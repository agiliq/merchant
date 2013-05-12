import urllib
import urllib2
import datetime

from collections import namedtuple

from django.conf import settings
from django.template.loader import render_to_string

from billing.models import AuthorizeAIMResponse
from billing import Gateway, GatewayNotConfigured
from billing.signals import *
from billing.utils.credit_card import InvalidCard, Visa, \
    MasterCard, Discover, AmericanExpress
from billing.utils.xml_parser import parseString, nodeToDic

API_VERSION = '3.1'
DELIM_CHAR = ','
ENCAP_CHAR = '$'
APPROVED, DECLINED, ERROR, FRAUD_REVIEW = 1, 2, 3, 4
RESPONSE_CODE, RESPONSE_REASON_CODE, RESPONSE_REASON_TEXT = 0, 2, 3

MockAuthorizeAIMResponse = namedtuple(
    'AuthorizeAIMResponse', [
        'response_code',
        'response_reason_code',
        'response_reason_text'
    ]
)


def save_authorize_response(response):
    data = {}
    data['response_code'] = int(response[0])
    data['response_reason_code'] = response[2]
    data['response_reason_text'] = response[3]
    data['authorization_code'] = response[4]
    data['address_verification_response'] = response[5]
    data['transaction_id'] = response[6]
    data['invoice_number'] = response[7]
    data['description'] = response[8]
    data['amount'] = response[9]
    data['method'] = response[10]
    data['transaction_type'] = response[11]
    data['customer_id'] = response[12]

    data['first_name'] = response[13]
    data['last_name'] = response[14]
    data['company'] = response[15]
    data['address'] = response[16]
    data['city'] = response[17]
    data['state'] = response[18]
    data['zip_code'] = response[19]
    data['country'] = response[20]
    data['phone'] = response[21]
    data['fax'] = response[22]
    data['email'] = response[23]

    data['shipping_first_name'] = response[24]
    data['shipping_last_name'] = response[25]
    data['shipping_company'] = response[26]
    data['shipping_address'] = response[27]
    data['shipping_city'] = response[28]
    data['shipping_state'] = response[29]
    data['shipping_zip_code'] = response[30]
    data['shipping_country'] = response[31]
    data['card_code_response'] = response[38]
    return AuthorizeAIMResponse.objects.create(**data)


class AuthorizeNetGateway(Gateway):
    test_url = "https://test.authorize.net/gateway/transact.dll"
    live_url = "https://secure.authorize.net/gateway/transact.dll"

    arb_test_url = 'https://apitest.authorize.net/xml/v1/request.api'
    arb_live_url = 'https://api.authorize.net/xml/v1/request.api'

    supported_countries = ["US"]
    default_currency = "USD"

    supported_cardtypes = [Visa, MasterCard, AmericanExpress, Discover]
    homepage_url = "http://www.authorize.net/"
    display_name = "Authorize.Net"

    def __init__(self):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("authorize_net"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        authorize_net_settings = merchant_settings["authorize_net"]
        self.login = authorize_net_settings["LOGIN_ID"]
        self.password = authorize_net_settings["TRANSACTION_KEY"]

    def add_invoice(self, post, options):
        """add invoice details to the request parameters"""
        post['invoice_num'] = options.get('order_id', None)
        post['description'] = options.get('description', None)

    def add_creditcard(self, post, credit_card):
        """add credit card details to the request parameters"""
        post['card_num'] = credit_card.number
        post['card_code'] = credit_card.verification_value
        post['exp_date'] = credit_card.expire_date
        post['first_name'] = credit_card.first_name
        post['last_name'] = credit_card.last_name

    def add_address(self, post, options):
        """add billing/shipping address details to the request parameters"""
        if options.get('billing_address', None):
            address = options.get('billing_address')
            post['address'] = address.get('address1', '') + \
                               address.get('address2', '')
            post['company'] = address.get('company', '')
            post['phone'] = address.get('phone', '')
            post['zip'] = address.get('zip', '')
            post['city'] = address.get('city', '')
            post['country'] = address.get('country', '')
            post['state'] = address.get('state', '')

        if options.get('shipping_address', None):
            address = options.get('shipping_address')
            post['ship_to_first_name'] = address.get('name', '').split(" ")[0]
            post['ship_to_last_name'] = " ".join(address.get('name', '').split(" ")[1:])
            post['ship_to_address'] = address.get('address1', '') + \
                                         address.get('address2', '')
            post['ship_to_company'] = address.get('company', '')
            post['ship_to_phone'] = address.get('phone', '')
            post['ship_to_zip'] = address.get('zip', '')
            post['ship_to_city'] = address.get('city', '')
            post['ship_to_country'] = address.get('country', '')
            post['ship_to_state'] = address.get('state', '')

    def add_customer_data(self, post, options):
        """add customer details to the request parameters"""
        if 'email' in options:
            post['email'] = options['email']
            post['email_customer'] = bool(options.get('email_customer', True))

        if 'customer' in options:
            post['cust_id'] = options['customer']

        if 'ip' in options:
            post['customer_ip'] = options['ip']

    @property
    def service_url(self):
        if self.test_mode:
            return self.test_url
        return self.live_url

    def commit(self, action, money, parameters):
        if not action == 'VOID':
            parameters['amount'] = money

        parameters['test_request'] = self.test_mode
        url = self.service_url
        data = self.post_data(action, parameters)
        response = self.request(url, data)
        return response

    def post_data(self, action, parameters=None):
        """add API details, gateway response formating options
        to the request parameters"""
        if not parameters:
            parameters = {}
        post = {}

        post['version'] = API_VERSION
        post['login'] = self.login
        post['tran_key'] = self.password
        post['relay_response'] = "FALSE"
        post['type'] = action
        post['delim_data'] = "TRUE"
        post['delim_char'] = DELIM_CHAR
        post['encap_char'] = ENCAP_CHAR

        post.update(parameters)
        return urllib.urlencode(dict(('x_%s' % (k), v) for k, v in post.iteritems()))

    # this shoud be moved to a requests lib file
    def request(self, url, data, headers=None):
        """Make POST request to the payment gateway with the data and return
        gateway RESPONSE_CODE, RESPONSE_REASON_CODE, RESPONSE_REASON_TEXT"""
        if not headers:
            headers = {}
        conn = urllib2.Request(url=url, data=data, headers=headers)
        try:
            open_conn = urllib2.urlopen(conn)
            response = open_conn.read()
        except urllib2.URLError as e:
            return MockAuthorizeAIMResponse(5, '1', str(e))
        fields = response[1:-1].split('%s%s%s' % (ENCAP_CHAR, DELIM_CHAR, ENCAP_CHAR))
        return save_authorize_response(fields)

    def purchase(self, money, credit_card, options=None):
        """Using Authorize.net payment gateway, charge the given
        credit card for specified money"""
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        post = {}
        self.add_invoice(post, options)
        self.add_creditcard(post, credit_card)
        self.add_address(post, options)
        self.add_customer_data(post, options)

        response = self.commit("AUTH_CAPTURE", money, post)
        status = "SUCCESS"
        if response.response_code != 1:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=response)
        else:
            transaction_was_successful.send(sender=self,
                                            type="purchase",
                                            response=response)
        return {"status": status, "response": response}

    def authorize(self, money, credit_card, options=None):
        """Using Authorize.net payment gateway, authorize the
        credit card for specified money"""
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        post = {}
        self.add_invoice(post, options)
        self.add_creditcard(post, credit_card)
        self.add_address(post, options)
        self.add_customer_data(post, options)

        response = self.commit("AUTH_ONLY", money, post)
        status = "SUCCESS"
        if response.response_code != 1:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="authorization",
                                              response=response)
        else:
            transaction_was_successful.send(sender=self,
                                            type="authorization",
                                            response=response)
        return {"status": status, "response": response}

    def capture(self, money, authorization, options=None):
        """Using Authorize.net payment gateway, capture the
        authorize credit card"""
        if not options:
            options = {}
        post = {}
        post["trans_id"] = authorization
        post.update(options)

        response = self.commit("PRIOR_AUTH_CAPTURE", money, post)
        status = "SUCCESS"
        if response.response_code != 1:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="capture",
                                              response=response)
        else:
            transaction_was_successful.send(sender=self,
                                            type="capture",
                                            response=response)
        return {"status": status, "response": response}

    def void(self, identification, options=None):
        """Using Authorize.net payment gateway, void the
        specified transaction"""
        if not options:
            options = {}
        post = {}
        post["trans_id"] = identification
        post.update(options)

        # commit ignores the money argument for void, so we set it None
        response = self.commit("VOID", None, post)
        status = "SUCCESS"
        if response.response_code != 1:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="void",
                                              response=response)
        else:
            transaction_was_successful.send(sender=self,
                                            type="void",
                                            response=response)
        return {"status": status, "response": response}

    def credit(self, money, identification, options=None):
        """Using Authorize.net payment gateway, void the
        specified transaction"""
        if not options:
            options = {}
        post = {}
        post["trans_id"] = identification
        # Authorize.Net requuires the card or the last 4 digits be sent
        post["card_num"] = options["credit_card"]
        post.update(options)

        response = self.commit("CREDIT", money, post)
        status = "SUCCESS"
        if response.response_code != 1:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="credit",
                                              response=response)
        else:
            transaction_was_successful.send(sender=self,
                                            type="credit",
                                            response=response)
        return {"status": status, "response": response}

    def recurring(self, money, credit_card, options):
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        template_vars = {}
        template_vars['auth_login'] = self.login
        template_vars['auth_key'] = self.password
        template_vars['amount'] = money
        template_vars['card_number'] = credit_card.number
        template_vars['exp_date'] = credit_card.expire_date

        template_vars['start_date'] = options.get('start_date') or datetime.date.today().strftime("%Y-%m-%d")
        template_vars['total_occurrences'] = options.get('total_occurences', 9999)
        template_vars['interval_length'] = options.get('interval_length', 1)
        template_vars['interval_unit'] = options.get('interval_unit', 'months')
        template_vars['sub_name'] = options.get('sub_name', '')
        template_vars['first_name'] = credit_card.first_name
        template_vars['last_name'] = credit_card.last_name

        xml = render_to_string('billing/arb/arb_create_subscription.xml', template_vars)

        if self.test_mode:
            url = self.arb_test_url
        else:
            url = self.arb_live_url
        headers = {'content-type': 'text/xml'}

        conn = urllib2.Request(url=url, data=xml, headers=headers)
        try:
            open_conn = urllib2.urlopen(conn)
            xml_response = open_conn.read()
        except urllib2.URLError as e:
            return MockAuthorizeAIMResponse(5, '1', str(e))

        response = nodeToDic(parseString(xml_response))['ARBCreateSubscriptionResponse']
        # successful response
        # {u'ARBCreateSubscriptionResponse': {u'messages': {u'message': {u'code': u'I00001',
        #                                                               u'text': u'Successful.'},
        #                                                  u'resultCode': u'Ok'},
        #                                    u'subscriptionId': u'933728'}}

        status = "SUCCESS"
        if response['messages']['resultCode'].lower() != 'ok':
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=response)
        else:
            transaction_was_successful.send(sender=self,
                                            type="recurring",
                                            response=response)
        return {"status": status, "response": response}

    def store(self, creditcard, options=None):
        raise NotImplementedError

    def unstore(self, identification, options=None):
        raise NotImplementedError
