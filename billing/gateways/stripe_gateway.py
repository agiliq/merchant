from billing import Gateway
from billing.gateway import InvalidData
from billing.signals import *
from billing.utils.credit_card import InvalidData,Visa,MasterCard,\
     AmericanExpress,Discover
import stripe

class StripePaymentGateway(Gateway):
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
                amount=amount,
                currency="usd",
                card={
                   'number':credit_card.number,
                   'exp_month':credit_card.month,
                   'exp_year':credit_card.year,
                   'cvc': credit_card.verification_value
                   
                },)
        except self.stripe.CardError, error:
            return error
        return response

    
    
    
    
