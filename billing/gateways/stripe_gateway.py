from billing import Gateway, GatewayNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import InvalidCard, Visa, MasterCard, \
     AmericanExpress, Discover, CreditCard
import stripe
from django.conf import settings


class StripeGateway(Gateway):
    supported_cardtypes = [Visa, MasterCard, AmericanExpress, Discover]
    supported_countries = ['US']
    default_currency = "USD"
    homepage_url = "https://stripe.com/"
    display_name = "Stripe"

    def __init__(self):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("stripe"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        stripe_settings = merchant_settings["stripe"]
        stripe.api_key = stripe_settings['API_KEY']
        self.stripe = stripe

    def purchase(self, amount, credit_card, options=None):
        card = credit_card
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            card = {
                'number': credit_card.number,
                'exp_month': credit_card.month,
                'exp_year': credit_card.year,
                'cvc': credit_card.verification_value
                }
        try:
            response = self.stripe.Charge.create(
                amount=int(amount * 100),
                currency=self.default_currency.lower(),
                card=card)
        except self.stripe.CardError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="purchase",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def store(self, credit_card, options=None):
        card = credit_card
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            card = {
                'number': credit_card.number,
                'exp_month': credit_card.month,
                'exp_year': credit_card.year,
                'cvc': credit_card.verification_value
                }
        try:
            customer = self.stripe.Customer.create(card=card)
        except (self.stripe.CardError, self.stripe.InvalidRequestError), error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="store",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="store",
                                        response=customer)
        return {'status': 'SUCCESS', 'response': customer}

    def recurring(self, credit_card, options=None):
        card = credit_card
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            card = {
                'number': credit_card.number,
                'exp_month': credit_card.month,
                'exp_year': credit_card.year,
                'cvc': credit_card.verification_value
                }
        try:
            plan_id = options['plan_id']
            self.stripe.Plan.retrieve(options['plan_id'])
            try:
                response = self.stripe.Customer.create(
                    card=card,
                    plan=plan_id
                )
                transaction_was_successful.send(sender=self,
                                                type="recurring",
                                                response=response)
                return {"status": "SUCCESS", "response": response}
            except self.stripe.CardError, error:
                transaction_was_unsuccessful.send(sender=self,
                                                  type="recurring",
                                                  response=error)
                return {"status": "FAILURE", "response": error}
        except self.stripe.InvalidRequestError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=error)
            return {"status": "FAILURE", "response": error}
        except TypeError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=error)
            return {"status": "FAILURE", "response": "Missing Plan Id"}

    def unstore(self, identification, options=None):
        try:
            customer = self.stripe.Customer.retrieve(identification)
            response = customer.delete()
            transaction_was_successful.send(sender=self,
                                              type="unstore",
                                              response=response)
            return {"status": "SUCCESS", "response": response}
        except self.stripe.InvalidRequestError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="unstore",
                                              response=error)
            return {"status": "FAILURE", "response": error}

    def credit(self, identification, money=None, options=None):
        try:
            charge = self.stripe.Charge.retrieve(identification)
            response = charge.refund(amount=money)
            transaction_was_successful.send(sender=self,
                                            type="credit",
                                            response=response)
            return {"status": "SUCCESS", "response": response}
        except self.stripe.InvalidRequestError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="credit",
                                              response=error)
            return {"status": "FAILURE", "error": error}

    def authorize(self, money, credit_card, options=None):
        card = credit_card
        if isinstance(credit_card, CreditCard):
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")
            card = {
                'number': credit_card.number,
                'exp_month': credit_card.month,
                'exp_year': credit_card.year,
                'cvc': credit_card.verification_value
                }
        try:
            token = self.stripe.Token.create(
                card=card,
                amount=int(money * 100),
            )
            transaction_was_successful.send(sender=self,
                                            type="authorize",
                                            response=token)
            return {'status': "SUCCESS", "response": token}
        except self.stripe.InvalidRequestError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="authorize",
                                              response=error)
            return {"status": "FAILURE", "response": error}

    def capture(self, money, authorization, options=None):
        try:
            response = self.stripe.Charge.create(
                amount=int(money * 100),
                card=authorization,
                currency=self.default_currency.lower()
            )
            transaction_was_successful.send(sender=self,
                                            type="capture",
                                            response=response)
            return {'status': "SUCCESS", "response": response}
        except self.stripe.InvalidRequestError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="capture",
                                              response=error)
            return {"status": "FAILURE", "response": error}
