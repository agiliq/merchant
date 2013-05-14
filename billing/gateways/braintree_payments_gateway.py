from billing import Gateway, GatewayNotConfigured
from billing.gateway import InvalidData
from billing.signals import *
from billing.utils.credit_card import InvalidCard, Visa, MasterCard, \
    AmericanExpress, Discover, CreditCard
from django.conf import settings
import braintree


class BraintreePaymentsGateway(Gateway):
    supported_cardtypes = [Visa, MasterCard, AmericanExpress, Discover]
    supported_countries = ["US"]
    default_currency = "USD"
    homepage_url = "http://www.braintreepayments.com/"
    display_name = "Braintree Payments"

    def __init__(self):
        test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)
        if test_mode:
            env = braintree.Environment.Sandbox
        else:
            env = braintree.Environment.Production
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("braintree_payments"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        braintree_settings = merchant_settings['braintree_payments']
        braintree.Configuration.configure(
            env,
            braintree_settings['MERCHANT_ACCOUNT_ID'],
            braintree_settings['PUBLIC_KEY'],
            braintree_settings['PRIVATE_KEY']
            )

    def _cc_expiration_date(self, credit_card):
        return "%s/%s" % (credit_card.month, credit_card.year)

    def _cc_cardholder_name(self, credit_card):
        return "%s %s" % (credit_card.first_name, credit_card.last_name)

    def _build_request_hash(self, options):
        request_hash = {
                "order_id": options.get("order_id", ""),
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

    def purchase(self, money, credit_card, options=None):
        if not options:
            options = {}
        if isinstance(credit_card, CreditCard) and not self.validate_card(credit_card):
             raise InvalidCard("Invalid Card")

        request_hash = self._build_request_hash(options)
        request_hash["amount"] = money

        if options.get("merchant_account_id"):
            request_hash["merchant_account_id"] = options.get("merchant_account_id")

        if isinstance(credit_card, CreditCard):
            request_hash["credit_card"] = {
                "number": credit_card.number,
                "expiration_date": self._cc_expiration_date(credit_card),
                "cardholder_name": self._cc_cardholder_name(credit_card),
                "cvv": credit_card.verification_value,
            }
        else:
            request_hash["payment_method_token"] = credit_card

        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        request_hash = self._build_request_hash(options)
        request_hash["amount"] = money
        request_hash["credit_card"] = {
            "number": credit_card.number,
            "expiration_date": self._cc_expiration_date(credit_card),
            "cardholder_name": self._cc_cardholder_name(credit_card),
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

    def authorize(self, money, credit_card, options=None):
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        request_hash = self._build_request_hash(options)
        request_hash["amount"] = money
        request_hash["credit_card"] = {
            "number": credit_card.number,
            "expiration_date": self._cc_expiration_date(credit_card),
            "cardholder_name": self._cc_cardholder_name(credit_card),
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

    def capture(self, money, authorization, options=None):
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

    def void(self, identification, options=None):
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

    def credit(self, money, identification, options=None):
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

    def recurring(self, money, credit_card, options=None):
        resp = self.store(credit_card, options=options)
        if resp["status"] == "FAILURE":
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=resp)
            return resp
        payment_token = resp["response"].customer.credit_cards[0].token
        request_hash = options["recurring"]
        request_hash.update({
            "payment_method_token": payment_token,
            })
        response = braintree.Subscription.create(request_hash)
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self,
                                            type="recurring",
                                            response=response)
        else:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=response)
        return {"status": status, "response": response}

    def store(self, credit_card, options=None):
        if not options:
            options = {}

        customer = options.get("customer", None)
        if not customer:
            raise InvalidData("Customer information needs to be passed.")

        try:
            first_name, last_name = customer["name"].split(" ", 1)
        except ValueError:
            first_name = customer["name"]
            last_name = ""

        search_resp = braintree.Customer.search(
            braintree.CustomerSearch.cardholder_name == credit_card.name,
            braintree.CustomerSearch.credit_card_number.starts_with(credit_card.number[:6]),
            braintree.CustomerSearch.credit_card_number.ends_with(credit_card.number[-4:]),
            braintree.CustomerSearch.credit_card_expiration_date == self._cc_expiration_date(credit_card)
            )

        customer_list = []
        for customer in search_resp.items:
            customer_list.append(customer)

        if len(customer_list) >= 1:
            # Take the first customer
            customer = customer_list[0]
        else:
            card_hash = {
                "number": credit_card.number,
                "expiration_date": self._cc_expiration_date(credit_card),
                "cardholder_name": self._cc_cardholder_name(credit_card),
                }

            if options.get("options"):
                card_hash["options"] = options["options"]

            request_hash = {
                "first_name": first_name,
                "last_name": last_name,
                "company": customer.get("company", ""),
                "email": customer.get("email", options.get("email", "")),
                "phone": customer.get("phone", ""),
                "credit_card": card_hash,
                }
            result = braintree.Customer.create(request_hash)
            if not result.is_success:
                transaction_was_unsuccessful.send(sender=self,
                                                  type="store",
                                                  response=result)
                return {"status": "FAILURE", "response": result}
            customer = result.customer

        request_hash = {}
        if options.get("billing_address"):
            name = options["billing_address"].get("name", "")
            try:
                first_name, last_name = name.split(" ", 1)
            except ValueError:
                first_name = name
                last_name = ""

            request_hash.update({
                "first_name": first_name,
                "last_name": last_name,
                "company":  options["billing_address"].get("company", ""),
                "street_address":  options["billing_address"].get("address1", ""),
                "extended_address":  options["billing_address"].get("address2", ""),
                "locality":  options["billing_address"].get("city", ""),
                "region":  options["billing_address"].get("state", ""),
                "postal_code":  options["billing_address"].get("zip", ""),
                "country_name":  options["billing_address"].get("country", "")
                })

        card_hash = {
            "number": credit_card.number,
            "expiration_date": self._cc_expiration_date(credit_card),
            "cardholder_name": self._cc_cardholder_name(credit_card),
            "options": {
                "update_existing_token": customer.credit_cards[0].token,
                }
            }
        if options.get("options"):
            card_hash["options"].update(options["options"])
        if request_hash:
            card_hash.update({"billing_address": request_hash})
        response = braintree.Customer.update(customer.id, {
                "credit_card": card_hash,
                })
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self,
                                            type="store",
                                            response=response)
        else:
            for ii in response.errors.deep_errors:
                print ii.message
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="store",
                                              response=response)
        return {"status": status, "response": response}

    def unstore(self, identification, options=None):
        response = braintree.CreditCard.delete(identification)
        if response.is_success:
            status = "SUCCESS"
            transaction_was_successful.send(sender=self,
                                            type="unstore",
                                            response=response)
        else:
            status = "FAILURE"
            transaction_was_unsuccessful.send(sender=self,
                                              type="unstore",
                                              response=response)
        return {"status": status, "response": response}
