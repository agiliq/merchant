
import urllib
import urllib2

API_VERSION = '3.1'
DELIM_CHAR = ','
ENCAP_CHAR = '$'
APPROVED, DECLINED, ERROR, FRAUD_REVIEW = 1, 2, 3, 4
RESPONSE_CODE, RESPONSE_REASON_CODE, RESPONSE_REASON_TEXT = 0, 2, 3


class AuthorizeNetGateway:
    def __init__(self, login, password, test_mode=True):
        self.login = login
        self.password = password
        self.test_mode = test_mode
        self.test_url = "https://test.authorize.net/gateway/transact.dll"
        self.live_url = "https://secure.authorize.net/gateway/transact.dll"

        # self.arb_test_url = 'https://apitest.authorize.net/xml/v1/request.api'
        # self.arb_live_url = 'https://api.authorize.net/xml/v1/request.api'
    
    # def authorize(money, credit_card, options={}):
    def purchase(self, money, credit_card, options={}):
        post = {}
        
        self.add_invoice(post, options) 
        self.add_creditcard(post, credit_card) 
        self.add_address(post, options)
        self.add_customer_data(post, options)
        # self.add_duplicate_window(post)

        self.commit('AUTH_CAPTURE', money, post)
    
    def add_invoice(self, post, options):
        post['invoice_num'] = options.get('order_id', None)
        post['description'] = options.get('description', None)
    
    def add_creditcard(self, post, credit_card):
        post['card_num']   = credit_card.number
        post['card_code']  = credit_card.verification_value
        post['exp_date']   = credit_card.expire_date
        post['first_name'] = credit_card.first_name
        post['last_name']  = credit_card.last_name
    
    def add_address(self, post, options):
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
        if options.has_key('email'):
            post['email'] = options['email']
            post['email_customer'] = false
        
        if options.has_key('customer'):
            post['cust_id'] = options['customer']

        if options.has_key('ip'):
            post['customer_ip'] = options['ip']

    def commit(self, action, money, parameters):
        if not action == 'VOID':
            parameters['amount'] = money
        
        parameters[:test_request] =  self.test_mode
        url = self.test_url if self.test_mode else self.live_url
        data = self.post_data(action, parameters)
        response = self.request(url, data)
        return response

    def post_data(self, action, parameters = {}):
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
        d = {}
        for key, value in post.items():
            d['x_%s' % (key)] = value
        return urllib.urlencode(d)
    
    # this shoud be moved to a requests lib file
    def request(self, url, data, headers={}):
        conn = urllib2.Request(url=url, data=data, headers=headers)
        try:
            open_conn = urllib2.urlopen(conn)
            response = open_conn.read()
        except urllib2.URLError, ue:
            return (5, '1', 'Could not talk to payment gateway.')
        fields = response[1::-1].split('%s%s%s' % (ENCAP_CHAR, DELIM_CHAR, ENCAP_CHAR))
        return [int(fields[RESPONSE_CODE]),
                fields[RESPONSE_REASON_CODE],
                fields[RESPONSE_REASON_TEXT]]

"""
    params = urllib.urlencode(raw_params)
    headers = { 'content-type':'application/x-www-form-urlencoded',
                'content-length':len(params) }
    post_url = settings.AUTHNET_POST_URL
    post_path = settings.AUTHNET_POST_PATH
    cn = httplib.HTTPSConnection(post_url, httplib.HTTPS_PORT)
    cn.request('POST', post_path, params, headers)
    return cn.getresponse().read().split(delimiter)
"""