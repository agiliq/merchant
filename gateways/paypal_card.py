

class PaypalCardProcess:
    def __init__(self):
        pass
    
    def purchase(self, money, credit_card, options={}):
        # django-paypal direct payment required params
        # creditcardtype acct expdate cvv2 ipaddress firstname lastname street city state countrycode zip amt
        from paypal.pro.helpers import PayPalWPP
        wpp = PayPalWPP(options['request']) 
        params = {}
        
        params['creditcardtype'] = credit_card.card_type
        params['acct'] = credit_card.number
        params['expdate'] = credit_card.expire_date
        params['cvv2'] = credit_card.verification_value
        params['ipaddress'] = options['request'].META.get("REMOTE_ADDR", "")
        params['amt'] = money
        
        params['firstname'] = credit_card.first_name
        params['lastname'] = credit_card.last_name
        params['street'] = 'street'
        params['city'] = 'city'
        params['state'] = 'state'
        params['countrycode'] = 'countrycode'
        params['zip'] = 'zip'
        
        # params.update(item)
        response = wpp.doDirectPayment(params)
        return response