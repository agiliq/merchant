"""
Paypal DoDirectPayment API
"""

from billing import Gateway
from paypal.pro.helpers import PayPalWPP        

class PaypalGateway(Gateway):
    def __init__(self):
        pass
    
    def purchase(self, money, credit_card, options={}):
        """Using PAYPAL DoDirectPayment, charge the given
        credit card for specified money"""
        # item = {
        #     'inv': 'inv',
        #     'custom': 'custom',
        #     'next': 'http://www.example.com/next/',
        #     'returnurl': 'http://www.example.com/pay/',
        #     'cancelurl': 'http://www.example.com/cancel/'
        # }
        
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

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
        # TODO: Fix the status and remove the hardcoding above
        return {"status": , "response": response}

    def authorize(self, money, credit_card, options = {}):
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        raise NotImplementedError

    def capture(self, money, authorization, options = {}):
        raise NotImplementedError

    def void(self, identification, options = {}):
        raise NotImplementedError

    def credit(self, money, identification, options = {}):
        raise NotImplementedError

    def recurring(self, money, creditcard, options = {}):
        raise NotImplementedError

    def store(self, creditcard, options = {}):
        raise NotImplementedError

    def unstore(self, identification, options = {}):
        raise NotImplementedError
