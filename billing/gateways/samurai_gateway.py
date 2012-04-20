from billing import Gateway, GatewayNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import InvalidCard, Visa, MasterCard, \
     AmericanExpress, Discover, CreditCard
import samurai
import samurai.config as samurai_config
from samurai.payment_method import PaymentMethod
from samurai.processor import Processor
from samurai.transaction import Transaction
from django.conf import settings


class SamuraiGateway(Gateway):
    supported_cardtypes = [Visa, MasterCard, AmericanExpress, Discover]
    supported_countries = ['US']
    default_currency = "USD"
    homepage_url = "https://samurai.feefighters.com/"
    display_name = "Samurai"

    def __init__(self):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("samurai"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        samurai_settings = merchant_settings["samurai"]
        samurai_config.merchant_key = samurai_settings['MERCHANT_KEY']
        samurai_config.merchant_password = samurai_settings['MERCHANT_PASSWORD']
        samurai_config.processor_token = samurai_settings['PROCESSOR_TOKEN']
        self.samurai = samurai

    def purchase(self, money, credit_card):
        # Cases where token is directly sent for e.g. from Samurai.js
        payment_method_token = credit_card
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            pm = PaymentMethod.create(credit_card.number, credit_card.verification_value,
                                      credit_card.month, credit_card.year)
            payment_method_token = pm.payment_method_token
        response = Processor.purchase(payment_method_token, money)
        if response.errors:
            transaction_was_unsuccessful.send(sender=self, 
                                              type="purchase",
                                              response=response)
            return {'status': 'FAILURE', 'response': response}
        transaction_was_successful.send(sender=self, 
                                        type="purchase",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def authorize(self, money, credit_card, options=None):
        payment_method_token = credit_card
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            pm = PaymentMethod.create(credit_card.number, credit_card.verification_value, 
                                      credit_card.month, credit_card.year)
            payment_method_token = pm.payment_method_token
        response = Processor.authorize(payment_method_token, money)
        if response.errors:
            transaction_was_unsuccessful.send(sender=self, 
                                              type="authorize",
                                              response=response)
            return {'status': 'FAILURE', 'response': response}
        transaction_was_successful.send(sender=self, 
                                        type="authorize",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def capture(self, money, identification, options=None):
        trans = Transaction.find(identification)
        if not trans.errors:
            new_trans = trans.capture(money)
            transaction_was_successful.send(sender=self, 
                                            type="capture",
                                            response=trans)
            return{'status': "SUCCESS", "response": new_trans}
        transaction_was_unsuccessful.send(sender=self, 
                                          type="capture",
                                          response=trans)
        return{"status": "FAILURE", "response": trans}

    def void(self, identification, options=None):
        trans = Transaction.find(identification)
        if not trans.errors:
            new_trans = trans.void()
            transaction_was_successful.send(sender=self, 
                                            type="void",
                                            response=trans)
            return{'status': "SUCCESS", "response": new_trans}
        transaction_was_unsuccessful.send(sender=self, 
                                          type="void",
                                          response=trans)
        return{"status": "FAILURE", "response": trans}

    def credit(self, money, identification, options=None):
        trans = Transaction.find(identification)
        if not trans.errors:
            new_trans = trans.reverse(money)
            transaction_was_successful.send(sender=self, 
                                            type="credit",
                                            response=trans)
            return{'status': "SUCCESS", "response": new_trans}
        transaction_was_unsuccessful.send(sender=self, 
                                          type="credit",
                                          response=trans)
        return{"status": "FAILURE", "response": trans}

    def store(self, credit_card, options=None):
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            payment_method = PaymentMethod.create(credit_card.number, 
                                                        credit_card.verification_value, 
                                                        credit_card.month, credit_card.year)
        else:
            # Using the token which has to be retained
            payment_method = PaymentMethod.find(credit_card)
            if payment_method.errors:
                transaction_was_unsuccessful.send(sender=self, 
                                                  type="store",
                                                  response=payment_method)
                return {'status': 'FAILURE', 'response': payment_method}
        response = payment_method.retain()
        if response.errors:
            transaction_was_unsuccessful.send(sender=self, 
                                              type="store",
                                              response=response)
            return {'status': 'FAILURE', 'response': response}
        transaction_was_successful.send(sender=self, 
                                        type="store",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def unstore(self, identification, options=None):
        payment_method = PaymentMethod.find(identification)
        if payment_method.errors:
            transaction_was_unsuccessful.send(sender=self, 
                                              type="unstore",
                                              response=payment_method)
            return {"status": "FAILURE", "response": payment_method}
        payment_method = payment_method.redact()
        if payment_method.errors:
            transaction_was_unsuccessful.send(sender=self, 
                                              type="unstore",
                                              response=payment_method)
            return {"status": "FAILURE", "response": payment_method}
        transaction_was_successful.send(sender=self, 
                                        type="unstore",
                                        response=payment_method)
        return {"status": "SUCCESS", "response": payment_method}
