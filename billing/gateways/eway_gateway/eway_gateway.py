from billing import CreditCard
from billing import Gateway, GatewayNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import Visa, MasterCard, DinersClub, JCB, AmericanExpress, InvalidCard

from eway_api.client import RebillEwayClient, DirectPaymentClient
from eway_api.client import REBILL_TEST_URL, REBILL_LIVE_URL, HOSTED_TEST_URL, HOSTED_LIVE_URL, DIRECT_PAYMENT_TEST_URL, DIRECT_PAYMENT_LIVE_URL

from django.conf import settings


class EwayGateway(Gateway):
    default_currency = "AUD"
    supported_countries = ["AU"]
    supported_cardtypes = [Visa, MasterCard, AmericanExpress, DinersClub, JCB]
    homepage_url = "https://eway.com.au/"
    display_name = "eWay"

    def __init__(self):
        self.test_mode = getattr(settings, 'MERCHANT_TEST_MODE', True)
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("eway"):
            raise GatewayNotConfigured("The '%s' gateway is not correctly "
                                       "configured." % self.display_name)
        eway_settings = merchant_settings["eway"]
        self.customer_id = eway_settings['CUSTOMER_ID']
        if self.test_mode:
            self.rebill_url = REBILL_TEST_URL
            self.hosted_url = HOSTED_TEST_URL
            self.direct_payment_url = DIRECT_PAYMENT_TEST_URL
        else:
            self.rebill_url = REBILL_LIVE_URL
            self.hosted_url = HOSTED_LIVE_URL
            self.direct_payment_url = DIRECT_PAYMENT_LIVE_URL

        self.eway_username = eway_settings['USERNAME']
        self.eway_password = eway_settings['PASSWORD']

    def add_creditcard(self, hosted_customer, credit_card):
        """
            add credit card details to the request parameters
        """
        hosted_customer.CCNumber = credit_card.number
        hosted_customer.CCNameOnCard = credit_card.name
        hosted_customer.CCExpiryMonth = '%02d' % (credit_card.month)
        hosted_customer.CCExpiryYear = str(credit_card.year)[-2:]
        hosted_customer.FirstName = credit_card.first_name
        hosted_customer.LastName = credit_card.last_name

    def add_address(self, hosted_customer, options=None):
        """
            add address details to the request parameters
        """
        if not options:
            options = {}
        address = options.get("billing_address", {})
        hosted_customer.Title = address.get("salutation", "Mr./Ms.")
        hosted_customer.Address = address.get("address1", '') + address.get("address2", "")
        hosted_customer.Suburb = address.get("city")
        hosted_customer.State = address.get("state")
        hosted_customer.Company = address.get("company")
        hosted_customer.PostCode = address.get("zip")
        hosted_customer.Country = address.get("country")
        hosted_customer.Email = address.get("email")
        hosted_customer.Fax = address.get("fax")
        hosted_customer.Phone = address.get("phone")
        hosted_customer.Mobile = address.get("mobile")
        hosted_customer.CustomerRef = address.get("customer_ref")
        hosted_customer.JobDesc = address.get("job_desc")
        hosted_customer.Comments = address.get("comments")
        hosted_customer.URL = address.get("url")

    def add_customer_details(self, credit_card, customer_detail, options=None):
        """
            add customer details to the request parameters
        """
        if not options:
            options = {}
        customer = options.get("customer_details", {})
        customer_detail.CustomerRef = customer.get("customer_ref")
        customer_detail.CustomerTitle = customer.get("customer_salutation", "")
        customer_detail.CustomerFirstName = credit_card.first_name
        customer_detail.CustomerLastName = credit_card.last_name
        customer_detail.CustomerCompany = customer.get("customer_company", "")
        customer_detail.CustomerJobDesc = customer.get("customer_job_desc", "")
        customer_detail.CustomerEmail = customer.get("customer_email")
        customer_detail.CustomerAddress = customer.get("customer_address1", "") + customer.get("customer_address2", "")
        customer_detail.CustomerSuburb = customer.get("customer_city", "")
        customer_detail.CustomerState = customer.get("customer_state", "")
        customer_detail.CustomerPostCode = customer.get("customer_zip", "")
        customer_detail.CustomerCountry = customer.get("customer_country", "")
        customer_detail.CustomerPhone1 = customer.get("customer_phone1", "")
        customer_detail.CustomerPhone2 = customer.get("customer_phone2", "")
        customer_detail.CustomerFax = customer.get("customer_fax", "")
        customer_detail.CustomerURL = customer.get("customer_url")
        customer_detail.CustomerComments = customer.get("customer_comments", "")

    def add_rebill_details(self, rebill_detail, rebile_customer_id, credit_card, rebill_profile):
        """
            add customer details to the request parameters
        """
        rebill_detail.RebillCustomerID = rebile_customer_id
        rebill_detail.RebillInvRef = rebill_profile.get("rebill_invRef")
        rebill_detail.RebillInvDesc = rebill_profile.get("rebill_invDesc")
        rebill_detail.RebillCCName = credit_card.name
        rebill_detail.RebillCCNumber = credit_card.number
        rebill_detail.RebillCCExpMonth = '%02d' % (credit_card.month)
        rebill_detail.RebillCCExpYear = str(credit_card.year)[-2:]
        rebill_detail.RebillInitAmt = rebill_profile.get("rebill_initAmt")
        rebill_detail.RebillInitDate = rebill_profile.get("rebill_initDate")
        rebill_detail.RebillRecurAmt = rebill_profile.get("rebill_recurAmt")
        rebill_detail.RebillStartDate = rebill_profile.get("rebill_startDate")
        rebill_detail.RebillInterval = rebill_profile.get("rebill_interval")
        rebill_detail.RebillIntervalType = rebill_profile.get("rebill_intervalType")
        rebill_detail.RebillEndDate = rebill_profile.get("rebill_endDate")

    def add_direct_payment_details(self, credit_card, customer_details, payment_details):
        direct_payment_details = {}
        direct_payment_details['ewayCustomerID'] = self.customer_id
        direct_payment_details['ewayCustomerFirstName'] = customer_details.get('customer_fname', '')
        direct_payment_details['ewayCustomerLastName'] = customer_details.get('customer_lname', '')
        direct_payment_details['ewayCustomerAddress'] = customer_details.get('customer_address', '')
        direct_payment_details['ewayCustomerEmail'] = customer_details.get('customer_email', '')
        direct_payment_details['ewayCustomerPostcode'] = customer_details.get('customer_postcode', None)
        direct_payment_details['ewayCardNumber'] = credit_card.number
        direct_payment_details['ewayCardHoldersName'] = credit_card.name
        direct_payment_details['ewayCardExpiryMonth'] = '%02d' % (credit_card.month)
        direct_payment_details['ewayCardExpiryYear'] = str(credit_card.year)[-2:]
        direct_payment_details['ewayCVN'] = credit_card.verification_value
        direct_payment_details['ewayOption1'] = '',
        direct_payment_details['ewayOption2'] = '',
        direct_payment_details['ewayOption3'] = '',
        direct_payment_details['ewayTrxnNumber'] = payment_details.get('transaction_number', '')
        direct_payment_details['ewayTotalAmount'] = payment_details['amount']
        direct_payment_details['ewayCustomerInvoiceRef'] = payment_details.get('inv_ref', '')
        direct_payment_details['ewayCustomerInvoiceDescription'] = payment_details.get('inv_desc', '')
        return direct_payment_details

    @property
    def service_url(self):
        if self.test_mode:
            return HOSTED_TEST_URL
        return HOSTED_LIVE_URL

    def purchase(self, money, credit_card, options=None):
        """
            Using Eway payment gateway , charge the given
            credit card for specified money
        """
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")

        client = RebillEwayClient(customer_id=self.customer_id,
                                  username=self.eway_username,
                                  password=self.eway_password,
                                  url=self.service_url,
                                  )
        hosted_customer = client.client.factory.create("CreditCard")

        self.add_creditcard(hosted_customer, credit_card)
        self.add_address(hosted_customer, options)
        customer_id = client.create_hosted_customer(hosted_customer)

        pymt_response = client.process_payment(
            customer_id,
            money,
            options.get("invoice", 'test'),
            options.get("description", 'test')
        )

        if not hasattr(pymt_response, "ewayTrxnStatus"):
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=pymt_response)
            return {"status": "FAILURE", "response": pymt_response}

        if pymt_response.ewayTrxnStatus == "False":
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=pymt_response)
            return {"status": "FAILURE", "response": pymt_response}

        transaction_was_successful.send(sender=self,
                                        type="purchase",
                                        response=pymt_response)
        return {"status": "SUCCESS", "response": pymt_response}

    def authorize(self, money, credit_card, options=None):
        raise NotImplementedError

    def capture(self, money, authorization, options=None):
        raise NotImplementedError

    def void(self, identification, options=None):
        raise NotImplementedError

    def credit(self, money, identification, options=None):
        raise NotImplementedError

    def direct_payment(self, credit_card_details, options=None):
        """
            Function that implement Direct Payment functionality provided by eWay.
                (Reference: http://www.eway.com.au/developers/api/direct-payments)

            Input Parameters:
                ( Please find the details here in this Gist: https://gist.github.com/08893221533daad49388 )
                credit_card   :    Customer Credit Card details
                options       :    Customer and Recurring Payment details

            Output Paramters:
                status: 'SUCCESS' or 'FAILURE'
                response : eWay Response in Dictionary format.
        """
        error_response = {}
        try:
            if (options and options.get('customer_details', False) and
                    options.get('payment_details', False)):
                customer_details = options.get('customer_details')
                payment_details = options.get('payment_details')
            else:
                error_response = {"reason": "Not enough information Available!"}
                raise

            """
                # Validate Entered credit card details.
            """
            credit_card = CreditCard(**credit_card_details)
            is_valid = self.validate_card(credit_card)
            if not is_valid:
                raise InvalidCard("Invalid Card")

            """
                # Create direct payment details
            """
            direct_payment_details = self.add_direct_payment_details(credit_card, customer_details, payment_details)

            """
                Process Direct Payment.
            """
            dpObj = DirectPaymentClient(self.direct_payment_url)
            response = dpObj.process_direct_payment(direct_payment_details)

            """
                Return value based on eWay Response
            """
            eway_response = response.get('ewayResponse', None)
            if eway_response and eway_response.get('ewayTrxnStatus', 'false').lower() == 'true':
                status = "SUCCESS"
            else:
                status = "FAILURE"

        except Exception as e:
            error_response['exception'] = e
            return {"status": "FAILURE", "response": error_response}

        return {"status": status, "response": response}

    def recurring(self, credit_card_details, options=None):
        """
            Recurring Payment Implementation using eWay recurring API (http://www.eway.com.au/developers/api/recurring)

            Input Parameters:
                ( Please find the details here in this Gist: https://gist.github.com/df67e02f7ffb39f415e6 )
                credit_card   :    Customer Credit Card details
                options       :    Customer and Recurring Payment details

            Output Dict:
                status: 'SUCCESS' or 'FAILURE'
                response : Response list of rebill event request in order of provided input
                           in options["customer_rebill_details"] list.
        """
        error_response = {}
        try:
            if not options:
                error_response = {"reason": "Not enough information Available!"}
                raise

            """
                # Validate Entered credit card details.
            """
            credit_card = CreditCard(**credit_card_details)
            if not self.validate_card(credit_card):
                raise InvalidCard("Invalid Card")

            rebillClient = RebillEwayClient(
                customer_id=self.customer_id,
                username=self.eway_username,
                password=self.eway_password,
                url=self.rebill_url,
            )
            # CustomerDetails : To create rebill Customer
            customer_detail = rebillClient.client.factory.create("CustomerDetails")
            self.add_customer_details(credit_card, customer_detail, options)
            """
                # Create Rebill customer and retrieve customer rebill ID.
            """
            rebill_customer_response = rebillClient.create_rebill_customer(customer_detail)

            # Handler error in create_rebill_customer response
            if rebill_customer_response.ErrorSeverity:
                transaction_was_unsuccessful.send(sender=self,
                                                  type="recurringCreateRebill",
                                                  response=rebill_customer_response)
                error_response = rebill_customer_response
                raise

            rebile_customer_id = rebill_customer_response.RebillCustomerID
            """
                For Each rebill profile
                # Create Rebill events using rebill customer ID and customer rebill details.
            """
            rebill_event_response_list = []
            for each_rebill_profile in options.get("customer_rebill_details", []):
                rebill_detail = rebillClient.client.factory.create("RebillEventDetails")
                self.add_rebill_details(rebill_detail, rebile_customer_id, credit_card, each_rebill_profile)

                rebill_event_response = rebillClient.create_rebill_event(rebill_detail)

                # Handler error in create_rebill_event response
                if rebill_event_response.ErrorSeverity:
                    transaction_was_unsuccessful.send(sender=self,
                                                      type="recurringRebillEvent",
                                                      response=rebill_event_response)
                    error_response = rebill_event_response
                    raise

                rebill_event_response_list.append(rebill_event_response)

            transaction_was_successful.send(sender=self,
                                            type="recurring",
                                            response=rebill_event_response_list)
        except Exception as e:
            error_response['exception'] = e
            return {"status": "Failure", "response": error_response}

        return {"status": "SUCCESS", "response": rebill_event_response_list}

    def recurring_cancel(self, rebill_customer_id, rebill_id):
        """
            Recurring Payment Cancelation (http://www.eway.com.au/developers/api/recurring)

            Input Parameters:
                - rebill_customer_id,
                - rebill_id  ( Output of recurring method)

            Output Dict:
                status : 'SUCCESS' or 'FAILURE'
                response : Rebill/Recurring Cancelation Response from eWay Web service.
        """
        rebillDeleteClient = RebillEwayClient(
            customer_id=self.customer_id,
            username=self.eway_username,
            password=self.eway_password,
            url=self.rebill_url,
        )

        """
            # Delete Rebill Event, using customer create rebill detail.
        """
        delete_rebill_response = rebillDeleteClient.delete_rebill_event(rebill_customer_id, rebill_id)

        # Handler error in delete_rebill_customer response
        if delete_rebill_response.ErrorSeverity:
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurringDeleteRebill",
                                              response=delete_rebill_response)
            return {"status": "FAILURE", "response": delete_rebill_response}

        transaction_was_successful.send(sender=self,
                                        type="recurring",
                                        response=delete_rebill_response)
        return {"status": "SUCCESS", "response": delete_rebill_response}

    def store(self, creditcard, options=None):
        raise NotImplementedError

    def unstore(self, identification, options=None):
        raise NotImplementedError
