
class PaypalCardProcess:
    def __init__(self):
        pass
    
    def purchase(self, money, credit_card, options={}):
        from paypal.pro.helpers import PayPalWPP
        
        # item = {
        #     'inv': 'inv',
        #     'custom': 'custom',
        #     'next': 'http://www.example.com/next/',
        #     'returnurl': 'http://www.example.com/pay/',
        #     'cancelurl': 'http://www.example.com/cancel/'
        # }
        
        params = {}
        params['creditcardtype'] = credit_card.card_type
        params['acct'] = credit_card.number
        params['expdate'] = '%02d%04d' % (credit_card.month, credit_card.year)
        params['cvv2'] = credit_card.verification_value
        params['ipaddress'] = options['request'].META.get("REMOTE_ADDR", "")
        params['amt'] = money
        
        params['firstname'] = credit_card.first_name
        params['lastname'] = credit_card.last_name
        params['street'] = '1 Main St'
        params['city'] = 'SAn Jose'
        params['state'] = 'CA'
        params['countrycode'] = 'US'
        params['zip'] = '95131'
        
        # params.update(item)
        
        wpp = PayPalWPP(options['request']) 
        response = wpp.doDirectPayment(params)
        return (response.ack)