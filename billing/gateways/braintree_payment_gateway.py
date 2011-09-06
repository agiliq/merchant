from billing import Gateway
from billing.signals import *
from billing.utils.credit_card import InvalidCard
from django.conf import settings
import braintree

class BraintreePaymentGateway(Gateway):
    def _build_request_hash(self, options):
        request_hash = {
                "order_id": options.get("order_id", ""),
                "merchant_account_id": settings.BRAINTREE_MERCHANT_ACCOUNT_ID,
                }
        if options.get("customer"):
            name = options["customer"].get("name", "")
            try:
                first_name, last_name = name.split(" ", 1)
            except ValueError:
                first_name = name
                last_name = ""
            request_hash.update({
                "customer": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "company": options["customer"].get("company", ""),
                    "phone": options["customer"].get("phone", ""),
                    "fax": options["customer"].get("fax", ""),
                    "website": options["customer"].get("website", ""),
                    "email": options["customer"].get("email", options.get("email", ""))
                    }
                })
        if options.get("billing_address"):
            name = options["billing_address"].get("name", "")
            try:
                first_name, last_name = name.split(" ", 1)
            except ValueError:
                first_name = name
                last_name = ""
            request_hash.update({
                "billing": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "company": options["billing_address"].get("company", ""),
                    "street_address": options["billing_address"].get("address1", ""),
                    "extended_address": options["billing_address"].get("address2", ""),
                    "locality": options["billing_address"].get("city", ""),
                    "region": options["billing_address"].get("state", ""),
                    "postal_code": options["billing_address"].get("zip", ""),
                    "country_code_alpha2": options["billing_address"].get("country", "")
                    }
                })
        if options.get("shipping_address"):
            name = options["shipping_address"].get("name", "")
            try:
                first_name, last_name = name.split(" ", 1)
            except ValueError:
                first_name = name
                last_name = ""
            request_hash.update({
                "shipping": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "company": options["shipping_address"].get("company", ""),
                    "street_address": options["shipping_address"].get("address1", ""),
                    "extended_address": options["shipping_address"].get("address2", ""),
                    "locality": options["shipping_address"].get("city", ""),
                    "region": options["shipping_address"].get("state", ""),
                    "postal_code": options["shipping_address"].get("zip", ""),
                    "country_code_alpha2": options["shipping_address"].get("country", "")
                    }
                })
        return request_hash

    def purchase(self, money, credit_card, options = None):
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        request_hash = self._build_request_hash(options)
        request_hash["amount"] = money
        request_hash["credit_card"] = {
            "number": credit_card.number,
            "expiration_date": "%s/%s" %(credit_card.month,
                                         credit_card.year),
            "cardholder_name": "%s %s" %(credit_card.first_name,
                                         credit_card.last_name),
            "cvv": credit_card.verification_value,
            }
        braintree_options = options.get("options", {})
        braintree_options.update({"submit_for_settlement": True})
        request_hash.update({
                "options": braintree_options
                })
        response = braintree.Transaction.sale(request_hash)
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self, 
                                            type="purchase",
                                            response=response)
        else:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=response)
        return {"status": status, "response": response}

    def authorize(self, money, credit_card, options = None):
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        request_hash = self._build_request_hash(options)
        request_hash["amount"] = money
        request_hash["credit_card"] = {
            "number": credit_card.number,
            "expiration_date": "%s/%s" %(credit_card.month,
                                         credit_card.year),
            "cardholder_name": "%s %s" %(credit_card.first_name,
                                         credit_card.last_name),
            "cvv": credit_card.verification_value,
            }
        braintree_options = options.get("options", {})
        if braintree_options:
            request_hash.update({
                    "options": braintree_options
                    })
        response = braintree.Transaction.sale(request_hash)
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self, 
                                            type="authorize",
                                            response=response)
        else:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="authorize",
                                              response=response)
        return {"status": status, "response": response}

    def capture(self, money, authorization, options = None):
        response = braintree.Transaction.submit_for_settlement(authorization, money)
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self,
                                            type="capture",
                                            response=response)
        else:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="capture",
                                              response=response)
        return {"status": status, "response": response}

    def void(self, identification, options = None):
        response = braintree.Transaction.void(identification)
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self,
                                            type="void",
                                            response=response)
        else:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="void",
                                              response=response)
        return {"status": status, "response": response}

    def credit(self, money, identification, options = None):
        response = braintree.Transaction.refund(identification, money)
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self,
                                            type="credit",
                                            response=response)
        else:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="credit",
                                              response=response)
        return {"status": status, "response": response}

    def recurring(self, money, creditcard, options = None):
        pass

    def store(self, creditcard, options = None):
        pass

    def unstore(self, identification, options = None):
        pass
