from billing import Gateway, GatewayNotConfigured
import requests
from requests.auth import HTTPBasicAuth
from billing.signals import transaction_was_unsuccessful, \
    transaction_was_successful
from billing.utils.credit_card import CreditCard
from django.conf import settings

class ChargebeeGateway(Gateway):
    display_name = "Chargebee"
    homepage_url = "https://chargebee.com/"

    def __init__(self):
        test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("chargebee"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        chargebee_settings = merchant_settings["chargebee"]
        self.chargebee_api_key = chargebee_settings["API_KEY"]
        chargebee_site = chargebee_settings["SITE"]
        self.chargebee_api_base_url = "https://%s.chargebee.com/api/v1" % chargebee_site

    def _chargebee_request(self, method, url, **kwargs):
        request_method = getattr(requests, method)
        uri = "%s%s" % (self.chargebee_api_base_url, url)
        if kwargs.pop("requires_auth", True) and not kwargs.get("auth"):
            kwargs["auth"] = HTTPBasicAuth(self.chargebee_api_key, '')
        return request_method(uri, **kwargs)

    def purchase(self, money, credit_card, options = None):
        """Create a plan that bills every decade or so 
        and charge the plan immediately"""
        options = options or {}
        resp = self.store(credit_card, options = options)
        subscription_id = resp["response"]["subscription"]["id"]
        resp = self._chargebee_request("post", "/invoices/charge", 
                                       data = {"subscription_id": subscription_id,
                                               "amount": money,
                                               "description": options.get("description")})
        if 200 <= resp.status_code < 300:
            transaction_was_successful.send(sender=self,
                                            type="purchase",
                                            response=resp.json())
            return {'status': 'SUCCESS', 'response': resp.json()}
        transaction_was_unsuccessful.send(sender=self,
                                          type="purchase",
                                          response=resp.json())
        return {'status': 'FAILURE', 'response': resp.json()}
            

    def authorize(self, money, credit_card, options = None):
        """This is a mirror to the store method. Create a plan 
        that bills every decade or so for a large authorized
        amount and charge that plan with the capture method"""
        return self.store(credit_card, options = options)

    def capture(self, money, authorization, options = None):
        options = options or {}
        resp = self._chargebee_request("post", "/invoices/charge",
                                       data = {"subscription_id": authorization,
                                               "amount": money,
                                               "description": options.get("description")})
        if 200 <= resp.status_code < 300:
            transaction_was_successful.send(sender=self,
                                            type="capture",
                                            response=resp.json())
            return {'status': 'SUCCESS', 'response': resp.json()}
        transaction_was_unsuccessful.send(sender=self,
                                          type="capture",
                                          response=resp.json())
        return {'status': 'FAILURE', 'response': resp.json()}

    def void(self, identification, options = None):
        return self.unstore(identification, options = options)

    def recurring(self, money, credit_card, options = None):
        return self.store(credit_card, options = options)

    def store(self, credit_card, options = None):
        options = options or {}
        if isinstance(credit_card, CreditCard):
            options.update({"card[first_name]": credit_card.first_name,
                            "card[last_name]": credit_card.last_name,
                            "card[number]": credit_card.number,
                            "card[expiry_year]": credit_card.year,
                            "card[expiry_month]": credit_card.month,
                            "card[cvv]": credit_card.verification_value})
        resp = self._chargebee_request('post', "/subscriptions", data = options)
        if 200 <= resp.status_code < 300:
            transaction_was_successful.send(sender=self,
                                            type="store",
                                            response=resp.json())
            return {'status': 'SUCCESS', 'response': resp.json()}
        transaction_was_unsuccessful.send(sender=self,
                                          type="store",
                                          response=resp.json())
        return {'status': 'FAILURE', 'response': resp.json()}

    def unstore(self, identification, options = None):
        options = options or {}
        resp = self._chargebee_request('post',
                                       "/subscriptions/%s/cancel" % identification,
                                       data = options)
        if 200 <= resp.status_code < 300:
            transaction_was_successful.send(sender=self,
                                            type="void",
                                            response=resp.json())
            return {'status': 'SUCCESS', 'response': resp.json()}
        transaction_was_unsuccessful.send(sender=self,
                                          type="void",
                                          response=resp.json())
        return {'status': 'FAILURE', 'response': resp.json()}
