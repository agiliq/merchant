
import urllib
import urllib2

from django.conf import settings
from billing.models import AuthorizeAIMResponse

API_VERSION = '3.1'
DELIM_CHAR = ','
ENCAP_CHAR = '$'
APPROVED, DECLINED, ERROR, FRAUD_REVIEW = 1, 2, 3, 4
RESPONSE_CODE, RESPONSE_REASON_CODE, RESPONSE_REASON_TEXT = 0, 2, 3


def save_authorize_response(response):
    data = {}
    data['response_code']                 = int(response[0])
    data['response_reason_code']          = response[2]
    data['response_reason_text']          = response[3]
    data['authorization_code']            = response[4]
    data['address_verification_response'] = response[5]
    data['transaction_id']                = response[6]
    data['invoice_number']                = response[7]
    data['description']                   = response[8]
    data['amount']                        = response[9]
    data['method']                        = response[10]
    data['transaction_type']              = response[11]
    data['customer_id']                   = response[12]

    data['first_name'] = response[13]
    data['last_name']  = response[14]
    data['company']    = response[15]
    data['address']    = response[16]
    data['city']       = response[17]
    data['state']      = response[18]
    data['zip_code']   = response[19]
    data['country']    = response[20]
    data['phone']      = response[21]
    data['fax']        = response[22]
    data['email']      = response[23]


    data['shipping_first_name'] = response[24]
    data['shipping_last_name']  = response[25]
    data['shipping_company']    = response[26]
    data['shipping_address']    = response[27]
    data['shipping_city']       = response[28]
    data['shipping_state']      = response[29]
    data['shipping_zip_code']   = response[30]
    data['shipping_country']    = response[31]
 
    data['card_code_response'] = response[38]
    AuthorizeAIMResponse.objects.create(**data)
    

class AuthorizeNetGateway(object):
    def __init__(self):
        self.login = settings.AUTHORIZE_LOGIN_ID
        self.password = settings.AUTHORIZE_TRANSACTION_KEY
        self.test_mode = getattr(settings, 'MERCHANT_TEST_MODE', False)
        self.test_url = "https://test.authorize.net/gateway/transact.dll"
        self.live_url = "https://secure.authorize.net/gateway/transact.dll"

        # self.arb_test_url = 'https://apitest.authorize.net/xml/v1/request.api'
        # self.arb_live_url = 'https://api.authorize.net/xml/v1/request.api'
    
    def purchase(self, money, credit_card, options={}):
        """Using Authorize.net payment gateway , charge the given
        credit card for specified money"""
        post = {}
        
        self.add_invoice(post, options) 
        self.add_creditcard(post, credit_card) 
        self.add_address(post, options)
        self.add_customer_data(post, options)
        # self.add_duplicate_window(post)

        return self.commit('AUTH_CAPTURE', money, post)
    
    def add_invoice(self, post, options):
        """add invoice details to the request parameters"""
        post['invoice_num'] = options.get('order_id', None)
        post['description'] = options.get('description', None)
    
    def add_creditcard(self, post, credit_card):
        """add credit card details to the request parameters"""
        post['card_num']   = credit_card.number
        post['card_code']  = credit_card.verification_value
        post['exp_date']   = credit_card.expire_date
        post['first_name'] = credit_card.first_name
        post['last_name']  = credit_card.last_name
    
    def add_address(self, post, options):
        """add billing/shipping address details to the request parameters"""
        if options.get('billing_address', None):
            address = options.get('billing_address')
            post['address']  = address.get('address', '')
            post['company']  = address.get('company', '')
            post['phone']    = address.get('phone', '')
            post['zip']      = address.get('zip', '')
            post['city']     = address.get('city', '')
            post['country']  = address.get('country', '')
            post[':state']   = address.get('state', '')
          
        if options.get('shipping_address', None):
            address = options.get('shipping_address')
            post['ship_to_first_name'] = address.get('first_name', '')
            post['ship_to_last_name']  = address.get('last_name', '')
            post['ship_to_address']    = address.get('address', '')
            post['ship_to_company']    = address.get('company', '')
            post['ship_to_phone']      = address.get('phone', '')
            post['ship_to_zip']        = address.get('zip', '')
            post['ship_to_city']       = address.get('city', '')
            post['ship_to_country']    = address.get('country', '')
            post['ship_to_state']      = address.get('state', '')
    
    def add_customer_data(self, post, options):
        """add customer details to the request parameters"""
        if options.has_key('email'):
            post['email'] = options['email']
            post['email_customer'] = False
        
        if options.has_key('customer'):
            post['cust_id'] = options['customer']

        if options.has_key('ip'):
            post['customer_ip'] = options['ip']

    def commit(self, action, money, parameters):
        if not action == 'VOID':
            parameters['amount'] = money
        
        parameters['test_request'] =  self.test_mode
        url = self.test_url if self.test_mode else self.live_url
        data = self.post_data(action, parameters)
        response = self.request(url, data)
        return response

    def post_data(self, action, parameters = {}):
        """add API details, gateway response formating options 
        to the request parameters"""
        post = {}
        
        post['version']        = API_VERSION
        post['login']          = self.login
        post['tran_key']       = self.password
        post['relay_response'] = "FALSE"
        post['type']           = action
        post['delim_data']     = "TRUE"
        post['delim_char']     = DELIM_CHAR
        post['encap_char']     = ENCAP_CHAR
        
        post.update(parameters)
        return urllib.urlencode(dict(('x_%s' % (k), v) for k, v in post.iteritems()))
    
    # this shoud be moved to a requests lib file
    def request(self, url, data, headers={}):
        """Make POST request to the payment gateway with the data and return 
        gateway RESPONSE_CODE, RESPONSE_REASON_CODE, RESPONSE_REASON_TEXT"""
        conn = urllib2.Request(url=url, data=data, headers=headers)
        try:
            open_conn = urllib2.urlopen(conn)
            response = open_conn.read()
        except urllib2.URLError:
            return (5, '1', 'Could not talk to payment gateway.')
        fields = response[1:-1].split('%s%s%s' % (ENCAP_CHAR, DELIM_CHAR, ENCAP_CHAR))
        save_authorize_response(fields)
        return [fields[RESPONSE_CODE],
                fields[RESPONSE_REASON_CODE],
                fields[RESPONSE_REASON_TEXT]]
