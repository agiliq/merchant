from beanstream.gateway import Beanstream
from beanstream.billing import CreditCard
from beanstream.process_transaction import Adjustment

from django.conf import settings

from billing import Gateway, GatewayNotConfigured
from billing.gateway import CardNotSupported
from billing.signals import transaction_was_successful, \
    transaction_was_unsuccessful
from billing.utils.credit_card import InvalidCard, Visa, \
    MasterCard, Discover, AmericanExpress

class BeanstreamGateway(Gateway):
    txnurl = "https://www.beanstream.com/scripts/process_transaction.asp"
    profileurl = "https://www.beanstream.com/scripts/payment_profile.asp"
    display_name = "Beanstream"

    # A list of all the valid parameters, and which ones are required.
    params = [
        ("requestType", True), # BACKEND Enter requestType=BACKEND for the recommended server to server integration method. Note that server to server typically cannot be used when hosting forms in the Beanstream Secure Webspace.
        ("merchant_id", True), # 9-digits Beanstream assigns one merchant ID number for each processing currency. Include the 9-digit Beanstream ID number here. Additional accounts may also have been issued for special services. Complete one full integration for each of the merchant IDs issued.
        ("trnOrderNumber", False), # but Recommended 30 alphanumeric (a/n) characters Include a unique order reference number if desired. If no number is passed, Beanstream will place the default transaction identification number (trnId) in this field. Custom order numbers will be used in duplicate transaction error checking. Order numbers are also required for Server to Server transaction queries. Integrators that wish to use the query function should pass custom values.
        ("trnAmount", True), # In the format 0.00. Max 2 decimal places. Max 9 digits total. This is the total dollar value of the purchase. This should represent the total of all taxes, shipping charges and other product/service costs as applicable.

        ("errorPage", True), # URL (encoded). Max 128 a/n characters. Not for use with server to server integrations. If a standard transaction request contains errors in billing or credit card information, the customer's browser will be re-directed to this page. Error messages will prompt the user to correct their data.
        ("approvedPage", False), # URL (encoded). Unlimited a/n characters. Beanstream provides default approved or declined transaction pages. For a seamless transaction flow, design unique pages and specify the approved transaction redirection URL here.
        ("declinedPage", False), # URL (encoded). Unlimited a/n characters. Specify the URL for your custom declined transaction notification page here.

        ("trnCardOwner", True), #* Max 64 a/n characters This field must contain the full name of the card holder exactly as it appears on their credit card.
        ("trnCardNumber", True), # Max 20 digits Capture the customer's credit card number.
        ("trnExpMonth", True), # 2 digits (January = 01) The card expiry month with January as 01 and December as 12.
        ("trnExpYear", True), # 2 digits (2011=11) Card expiry years must be entered as a number less than 50. In combination, trnExpYear and trnExpMonth must reflect a date in the future.
        ("trnCardCvd", False), # 4 digits Amex, 3 digits all other cards. Include the three or four-digit CVD number from the back of the customer's credit card. This information may be made mandatory using the "Require CVD" option in the Beanstream Order Settings module.
        ("ordName", True), #* Max 64 a/n characters. Capture the first and last name of the customer placing the order. This may be different from trnCardOwner.
        ("ordEmailAddress", True), # Max 64 a/n characters in the format a@b.com. The email address specified here will be used for sending automated email receipts.
        ("ordPhoneNumber", True), #* Min 7 a/n characters Max 32 a/n characters Collect a customer phone number for order follow-up.
        ("ordAddress1", True), #* Max 64 a/n characters Collect a unique street address for billing purposes.
        ("ordAddress2", False), # Max 64 a/n characters An optional variable is available for longer addresses.
        ("ordCity", True), #* Max 32 a/n characters The customer's billing city.
        ("ordProvince", True), #* 2 characters Province and state ID codes in this variable must match one of the available province and state codes.
        ("ordPostalCode", True), #* 16 a/n characters Indicates the customer's postal code for billing purposes.
        ("ordCountry", True), #* 2 characters Country codes must match one of the available ISO country codes.

        ("termURL", True), # URL (encoded) Specify the URL where the bank response codes will be collected after enters their VBV or SecureCode pin on the banking portal.
        ("vbvEnabled", False), # 1 digit When VBV service has been activated, Beanstream will attempt VBV authentication on all transactions. Use this variable to override our default settings and process VBV on selected transactions only. Pass vbvEnabled=1 to enable VBV authentication with an order. Pass vbvEnabled=0 to bypass VBV authentication on specific orders.
        ("scEnabled", False), # 1 digit When SecureCode service has been activated, Beanstream will attempt SC authentication on all transactions. Use this variable to override our default settings and process SC on selected transactions only. Pass scEnabled=1 to enable SC authentication with an order. Pass scEnabled=0 to bypass SC authentication on specific orders.

        ("SecureXID", True), # 20 digits Include the 3D secure transaction identifier as issued by the bank following VBV or SecureCode authentication.
        ("SecureECI", True), # 1 digit Provide the ECI status. 5=transaction authenticated. 6= authentication attempted but not completed.
        ("SecireCAVV", True), # 40 a/n characters Include the cardholder authentication verification value as issued by the bank.
    ]

    def __init__(self, *args, **kwargs):
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("beanstream"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        beanstream_settings = merchant_settings["beanstream"]

        self.supported_cardtypes = [Visa, MasterCard, AmericanExpress, Discover]

        hash_validation = False
        if kwargs.get("hash_algorithm", beanstream_settings.get("HASH_ALGORITHM", None)):
            hash_validation = True

        self.beangw = Beanstream(
            hash_validation=hash_validation,
            require_billing_address=kwargs.get("require_billing_address", False),
            require_cvd=kwargs.get("require_cvd", False))

        merchant_id = kwargs.pop("merchant_id", beanstream_settings["MERCHANT_ID"])
        login_company = kwargs.pop("login_company", beanstream_settings["LOGIN_COMPANY"])
        login_user = kwargs.pop("login_user", beanstream_settings["LOGIN_USER"])
        login_password = kwargs.pop("login_password", beanstream_settings["LOGIN_PASSWORD"])
        kwargs["payment_profile_passcode"] = beanstream_settings.get("PAYMENT_PROFILE_PASSCODE", None)

        if hash_validation:
            if not kwargs.get("hash_algorithm"):
                kwargs["hash_algorithm"] = beanstream_settings["HASH_ALGORITHM"]
            if not kwargs.get("hashcode"):
                kwargs["hashcode"] = beanstream_settings["HASHCODE"]

        self.beangw.configure(
            merchant_id,
            login_company,
            login_user,
            login_password,
            **kwargs)

    def convert_cc(self, credit_card, validate=True):
        """Convert merchant.billing.utils.CreditCard to beanstream.billing.CreditCard"""
        card = CreditCard(
            credit_card.first_name + " " + credit_card.last_name,
            credit_card.number,
            credit_card.month, credit_card.year,
            credit_card.verification_value)
        if validate:
            self.validate_card(card)
        return card

    def _parse_resp(self, resp):
        status = "FAILURE"
        response = resp

        if resp.approved():
            status = "SUCCESS"

        return {"status": status, "response": response}

    def purchase(self, money, credit_card, options=None):
        """One go authorize and capture transaction"""
        options = options or {}
        txn = None
        order_number = options.get("order_number") if options else None

        if credit_card:
            card = self.convert_cc(credit_card)
            txn = self.beangw.purchase(money, card, None, order_number)
            billing_address = options.get("billing_address")
            if billing_address:
                txn.params.update({"ordName": billing_address["name"],
                                   "ordEmailAddress": billing_address["email"],
                                   "ordPhoneNumber": billing_address["phone"],
                                   "ordAddress1": billing_address["address1"],
                                   "ordAddress2": billing_address.get("address2", ""),
                                   "ordCity": billing_address["city"],
                                   "ordProvince": billing_address["state"],
                                   "ordCountry": billing_address["country"]})
        elif options.get("customer_code"):
            customer_code = options.get("customer_code", None)
            txn = self.beangw.purchase_with_payment_profile(money, customer_code, order_number)

        txn.validate()
        resp = self._parse_resp(txn.commit())
        if resp["status"] == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="purchase",
                                            response=resp["response"])
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=resp["response"])
        return resp

    def authorize(self, money, credit_card, options=None):
        """Authorization for a future capture transaction"""
        # TODO: Need to add check for trnAmount
        # For Beanstream Canada and TD Visa & MasterCard merchant accounts this value may be $0 or $1 or more.
        # For all other scenarios, this value must be $0.50 or greater.
        options = options or {}
        order_number = options.get("order_number") if options else None
        card = self.convert_cc(credit_card)
        txn = self.beangw.preauth(money, card, None, order_number)
        billing_address = options.get("billing_address")
        if billing_address:
            txn.params.update({"ordName": billing_address["name"],
                               "ordEmailAddress": billing_address["email"],
                               "ordPhoneNumber": billing_address["phone"],
                               "ordAddress1": billing_address["address1"],
                               "ordAddress2": billing_address.get("address2", ""),
                               "ordCity": billing_address["city"],
                               "ordProvince": billing_address["state"],
                               "ordCountry": billing_address["country"]})
        if options and "order_number" in options:
            txn.order_number = options.get("order_number");

        txn.validate()
        resp = self._parse_resp(txn.commit())
        if resp["status"] == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="authorize",
                                            response=resp["response"])
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="authorize",
                                              response=resp["response"])
        return resp

    def unauthorize(self, money, authorization, options=None):
        """Cancel a previously authorized transaction"""
        txn = Adjustment(self.beangw, Adjustment.PREAUTH_COMPLETION, authorization, money)

        resp = self._parse_resp(txn.commit())
        if resp["status"] == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="unauthorize",
                                            response=resp["response"])
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="unauthorize",
                                              response=resp["response"])
        return resp

    def capture(self, money, authorization, options=None):
        """Capture funds from a previously authorized transaction"""
        order_number = options.get("order_number") if options else None
        txn = self.beangw.preauth_completion(authorization, money, order_number)
        resp = self._parse_resp(txn.commit())
        if resp["status"] == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="capture",
                                            response=resp["response"])
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="capture",
                                              response=resp["response"])
        return resp

    def void(self, identification, options=None):
        """Null/Blank/Delete a previous transaction"""
        """Right now this only handles VOID_PURCHASE"""
        txn = self.beangw.void_purchase(identification["txnid"], identification["amount"])
        resp = self._parse_resp(txn.commit())
        if resp["status"] == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="void",
                                            response=resp["response"])
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="void",
                                              response=resp["response"])
        return resp

    def credit(self, money, identification, options=None):
        """Refund a previously 'settled' transaction"""
        order_number = options.get("order_number") if options else None
        txn = self.beangw.return_purchase(identification, money, order_number)
        resp = self._parse_resp(txn.commit())
        if resp["status"] == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="credit",
                                            response=resp["response"])
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="credit",
                                              response=resp["response"])
        return resp

    def recurring(self, money, creditcard, options=None):
        """Setup a recurring transaction"""
        card = self.convert_cc(creditcard)
        frequency_period = options['frequency_period']
        frequency_increment = options['frequency_increment']
        billing_address = options.get('billing_address', None) # must be a beanstream.billing.Address instance

        txn = self.beangw.create_recurring_billing_account(
            money, card, frequency_period, frequency_increment, billing_address)
        resp = self._parse_resp(txn.commit())
        if resp["status"] == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="recurring",
                                            response=resp["response"])
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=resp["response"])
        return resp

    def store(self, credit_card, options=None):
        """Store the credit card and user profile information
        on the gateway for future use"""
        card = self.convert_cc(credit_card)
        billing_address = options.get("billing_address")
        txn = self.beangw.create_payment_profile(card, billing_address)

        resp = txn.commit()

        status = "FAILURE"
        response = None
        if resp.approved() or resp.resp["responseCode"] == ["17"]:
            status = "SUCCESS"
        else:
            response = resp

        if status == "SUCCESS":
            transaction_was_successful.send(sender=self,
                                            type="recurring",
                                            response=response)
        else:
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurring",
                                              response=response)
        return {"status": status, "response": response}

    def unstore(self, identification, options=None):
        """Delete the previously stored credit card and user
        profile information on the gateway"""
        raise NotImplementedError
