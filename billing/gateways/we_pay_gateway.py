from billing import Gateway, GatewayNotConfigured
from billing.utils.credit_card import InvalidCard, Visa, MasterCard, CreditCard
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from django.conf import settings
from wepay import WePay
from wepay.exceptions import WePayError


class WePayGateway(Gateway):
    display_name = "WePay"
    homepage_url = "https://www.wepay.com/"
    default_currency = "USD"
    supported_countries = ["US"]
    supported_cardtypes = [Visa, MasterCard]

    def __init__(self):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("we_pay"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        super(WePayGateway, self).__init__()
        production = not self.test_mode
        self.we_pay = WePay(production)
        self.we_pay_settings = merchant_settings["we_pay"]

    def purchase(self, money, credit_card, options=None):
        options = options or {}
        params = {}
        params.update({
                'account_id': options.pop("account_id", self.we_pay_settings.get("ACCOUNT_ID", "")),
                'short_description': options.pop("description", ""),
                'amount': money,
                })
        if credit_card and not isinstance(credit_card, CreditCard):
            params["payment_method_id"] = credit_card
            params["payment_method_type"] = "credit_card"
        token = options.pop("access_token", self.we_pay_settings["ACCESS_TOKEN"])
        params.update(options)
        try:
            response = self.we_pay.call('/checkout/create', params, token=token)
        except WePayError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="purchase",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def authorize(self, money, credit_card, options=None):
        options = options or {}
        resp = self.store(credit_card, options)
        if resp["status"] == "FAILURE":
            transaction_was_unsuccessful.send(sender=self,
                                              type="authorize",
                                              response=resp['response'])
            return resp
        token = options.pop("access_token", self.we_pay_settings["ACCESS_TOKEN"])
        try:
            resp = self.we_pay.call('/credit_card/authorize', {
                    'client_id': self.we_pay_settings["CLIENT_ID"],
                    'client_secret': self.we_pay_settings["CLIENT_SECRET"],
                    'credit_card_id': resp['response']['credit_card_id']
                    }, token=token)
        except WePayError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="authorize",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        params = {
            "auto_capture": False
            }
        params.update(options)
        response = self.purchase(money, resp["credit_card_id"], params)
        if response["status"] == "FAILURE":
            transaction_was_unsuccessful.send(sender=self,
                                              type="authorize",
                                              response=response["response"])
            return response
        transaction_was_successful.send(sender=self,
                                        type="authorize",
                                        response=response["response"])
        return response

    def capture(self, money, authorization, options=None):
        options = options or {}
        params = {
            'checkout_id': authorization,
            }
        token = options.pop("access_token", self.we_pay_settings["ACCESS_TOKEN"])
        try:
            response = self.we_pay.call('/checkout/capture', params, token=token)
        except WePayError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="capture",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="capture",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def void(self, identification, options=None):
        options = options or {}
        params = {
            'checkout_id': identification,
            'cancel_reason': options.pop("description", "")
            }
        token = options.pop("access_token", self.we_pay_settings["ACCESS_TOKEN"])
        try:
            response = self.we_pay.call('/checkout/cancel', params, token=token)
        except WePayError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="void",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="void",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def credit(self, money, identification, options=None):
        options = options or {}
        params = {
            'checkout_id': identification,
            'refund_reason': options.pop("description", ""),
            }
        if money:
            params.update({'amount': money})
        token = options.pop("access_token", self.we_pay_settings["ACCESS_TOKEN"])
        try:
            response = self.we_pay.call('/checkout/refund', params, token=token)
        except WePayError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="credit",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="credit",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def recurring(self, money, credit_card, options=None):
        options = options or {}
        params = {
            'account_id': self.we_pay_settings.get("ACCOUNT_ID", ""),
            "short_description": options.pop("description", ""),
            "amount": money,
            }
        params.update(options)
        token = options.pop("access_token", self.we_pay_settings["ACCESS_TOKEN"])
        try:
            response = self.we_pay.call("/preapproval/create", params, token=token)
        except WePayError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="recurring",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}

    def store(self, credit_card, options=None):
        options = options or {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        token = options.pop("access_token", self.we_pay_settings["ACCESS_TOKEN"])
        try:
            response = self.we_pay.call('/credit_card/create', {
                    'client_id': self.we_pay_settings["CLIENT_ID"],
                    'user_name': credit_card.name,
                    'email': options.pop("customer")["email"],
                    'cc_number': credit_card.number,
                    'cvv': credit_card.verification_value,
                    'expiration_month': credit_card.month,
                    'expiration_year': credit_card.year,
                    'address': options.pop("billing_address")
                    }, token=token)
        except WePayError, error:
            transaction_was_unsuccessful.send(sender=self,
                                              type="store",
                                              response=error)
            return {'status': 'FAILURE', 'response': error}
        transaction_was_successful.send(sender=self,
                                        type="store",
                                        response=response)
        return {'status': 'SUCCESS', 'response': response}
