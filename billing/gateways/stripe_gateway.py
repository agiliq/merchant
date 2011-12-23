from billing import Gateway
from billing.gateway import InvalidData
from billing.signals import *
from billing.utils.credit_card import InvalidCard,Visa,MasterCard,\
     AmericanExpress,Discover
import stripe
from django.conf import settings
class StripeGateway(Gateway):
    supported_cardtypes = [Visa, MasterCard, AmericanExpress, Discover]
    supported_countries = ['US']
    default_currency = "USD"
    homepage_url = "https://stripe.com/"
    display_name = "Stripe"

    def __init__(self):
        stripe.api_key = settings.STRIPE_API_KEY
        self.stripe = stripe

    def purchase(self, amount, credit_card):
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        try:
            response = self.stripe.Charge.create(
                amount=amount*100,
                currency="usd",
                card={
                   'number':credit_card.number,
                   'exp_month':credit_card.month,
                   'exp_year':credit_card.year,
                   'cvc': credit_card.verification_value
                   
                },)
        except self.stripe.CardError, error:
            return {'status': 'FAILURE', 'response': error}
        return {'status': 'SUCCESS', 'response':response}
    
    def store(self, credit_card):
        customer = self.stripe.Customer.create (
                   card={
                   'number':credit_card.number,
                   'exp_month':credit_card.month,
                   'exp_year':credit_card.year,
                   'cvc': credit_card.verification_value
                    },
                    description = "Storing for future use"
        )
        return customer