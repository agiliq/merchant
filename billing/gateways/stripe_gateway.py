from billing import Gateway
from billing.gateway import InvalidData
from billing.signals import *
from billing.utils.credit_card import InvalidCard, Visa, MasterCard, \
     AmericanExpress, Discover
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
                amount=amount * 100,
                currency="usd",
                card={
                   'number': credit_card.number,
                   'exp_month': credit_card.month,
                   'exp_year': credit_card.year,
                   'cvc': credit_card.verification_value
                   },)
        except self.stripe.CardError, error:
            return {'status': 'FAILURE', 'response': error}
        return {'status': 'SUCCESS', 'response': response}

    def store(self, credit_card, options=None):
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        customer = self.stripe.Customer.create(
                   card={
                   'number': credit_card.number,
                   'exp_month': credit_card.month,
                   'exp_year': credit_card.year,
                   'cvc': credit_card.verification_value
                    },
                    description="Storing for future use"
        )
        return customer

    def recurring(self, credit_card, options=None):
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        response = None
        try:
            plan_id = options['plan_id']
            plan = self.stripe.Plan.retrieve(options['plan_id'])
            try:
                response = self.stripe.Customer.create(
                    card={
                        'number': credit_card.number,
                        'exp_month': credit_card.month,
                        'exp_year': credit_card.year,
                        'cvc': credit_card.verification_value
                    },
                    plan=options['plan_id'],
                    description="Thanks for subscribing"
                )
                return {"status": "SUCCESS", "response": response}
            except self.stripe.CardError, error:
                return {"status": "FAILED", "response": error}
        except self.stripe.InvalidRequestError, error:
            return {"status": "FAILED", "response": error}
        except TypeError:
            return {"status": "FAILED", "response": "please give a plan id"}

    def unstore(self, identification, options=None):
        try:
            customer = self.stripe.Customer.retrieve(identification)
            response = customer.delete()
            return {"status": "SUCCESS", "response": response}
        except self.stripe.InvalidRequestError, error:
            return {"status": "FAILED", "response": error}

    def credit(self, money, identification, options=None):
        try:
            charge = self.stripe.Charge.retrieve(identification)
            response = charge.refund(amount=money)
            return {"status": "SUCCESS", "response": response}
        except self.stripe.InvalidRequestError, error:
            return {"status": "FAILED", "error": error}
