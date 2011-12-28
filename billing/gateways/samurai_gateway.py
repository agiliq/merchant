from billing import Gateway
from billing.utils.credit_card import InvalidCard, Visa, MasterCard, \
     AmericanExpress, Discover
import samurai
from django.conf import settings

class SamuraiGateway(Gateway):
    supported_cardtypes = [Visa, MasterCard, AmericanExpress, Discover]
    supported_countries = ['US']
    default_currency = "USD"
    homepage_url = "https://samurai.feefighters.com/"
    display_name = "Samurai"

    def __init__(self):
        import samurai.config as config
        config.merchant_key = settings.SAMURAI_MERCHANT_KEY
        config.merchant_password = settings.SAMURAI_MERCHANT_PASSWORD
        config.processor_token = settings.SAMURAI_PROCESSOR_TOKEN
        self.samurai = samurai

    def purchase(self, money, credit_card):       
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        try:
            from samurai.payment_method import PaymentMethod
            from samurai.processor import Processor
            pm = PaymentMethod.create(credit_card.number, credit_card.verification_value, credit_card.month, credit_card.year)
            payment_method_token = pm.payment_method_token
            response = Processor.purchase(payment_method_token, money)
        except Exception, error:
            return {'status': 'FAILURE', 'response': error}
        return {'status': 'SUCCESS', 'response': response}
        
    def authorize(self, money, credit_card, options = None):
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        try:
            from samurai.payment_method import PaymentMethod
            from samurai.processor import Processor
            pm = PaymentMethod.create(credit_card.number, credit_card.verification_value, credit_card.month, credit_card.year)
            payment_method_token = pm.payment_method_token
            response = Processor.authorize(payment_method_token, money)
        except Exception, error:
            return {'status': 'FAILURE', 'response': error}
        return {'status': 'SUCCESS', 'response': response}
        
    def capture(self, money, identification, options = None):
        from samurai.transaction import Transaction
        trans = Transaction.find(identification)
        if not trans.errors:
            new_trans = trans.capture(money)
            return{'status': "SUCCESS", "response": new_trans}
        else:
            return{"status":"FAILED", "response": trans.errors}

    def reverse(self, money, authorization, options=None):
        if not authorization.errors:
            new_trans = authorization.reverse(money)
            return{'status': "SUCCESS", "response": new_trans}
        else:
            return{"status":"FAILED", "response": authorization.errors}

    def void(self, authorization, options=None):
        if not authorization.errors:
            new_trans = authorization.void()
            return{'status': "SUCCESS", "response": new_trans}
        else:
            return{"status":"FAILED", "response": authorization.errors}