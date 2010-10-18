
from django.conf import settings
from eway_api.client import RebillEwayClient, HOSTED_TEST_URL, HOSTED_LIVE_URL
from billing import Gateway
from billing.signals import *
from billing.utils.credit_card import Visa, MasterCard, DinersClub, JCB, AmericanExpress

TEST_URL     = 'https://www.eway.com.au/gateway/xmltest/testpage.asp'
LIVE_URL     = 'https://www.eway.com.au/gateway/xmlpayment.asp'

TEST_CVN_URL = 'https://www.eway.com.au/gateway_cvn/xmltest/testpage.asp'
LIVE_CVN_URL = 'https://www.eway.com.au/gateway_cvn/xmlpayment.asp'

class EwayGateway(Gateway):
    default_currency = "AUD"
    supported_countries = ["AU"]
    supported_cardtypes = [Visa, MasterCard, AmericanExpress, DinersClub, JCB]
    homepage_url = "https://eway.com.au/"
    display_name = "eWay"

    def __init__(self):
        self.test_mode = getattr(settings, 'MERCHANT_TEST_MODE', True)
        self.client = RebillEwayClient(test_mode=self.test_mode,
                                      customer_id=settings.EWAY_CUSTOMER_ID,
                                      username=settings.EWAY_USERNAME,
                                      password=settings.EWAY_PASSWORD,
                                      url=HOSTED_TEST_URL if self.test_mode else HOSTED_LIVE_URL,
                                      )
        self.hosted_customer = self.client.client.factory.create("CreditCard")
    
    def add_creditcard(self, credit_card):
        """add credit card details to the request parameters"""
        self.hosted_customer.CCNumber = credit_card.number
        self.hosted_customer.CCNameOnCard = credit_card.name
        self.hosted_customer.CCExpiryMonth = '%02d' % (credit_card.month)
        self.hosted_customer.CCExpiryYear = str(credit_card.year)[-2:]
        self.hosted_customer.FirstName = credit_card.first_name
        self.hosted_customer.LastName = credit_card.last_name
    
    def add_address(self, options={}):
        """add address details to the request parameters"""
        address = options["billing_address"]
        self.hosted_customer.Title = address.get("salutation", "Mr./Ms.")
        self.hosted_customer.Address = address["address1"] + address.get("address2", "")
        self.hosted_customer.Suburb = address.get("city")
        self.hosted_customer.State = address.get("state")
        self.hosted_customer.Company = address.get("company")
        self.hosted_customer.PostCode = address.get("zip")
        self.hosted_customer.Country = address.get("country")
        self.hosted_customer.Email = options.get("email")
        self.hosted_customer.Fax = address.get("fax")
        self.hosted_customer.Phone = address.get("phone")
        self.hosted_customer.Mobile = address.get("mobile")
        self.hosted_customer.CustomerRef = address.get("customer_ref")
        self.hosted_customer.JobDesc = address.get("job_desc")
        self.hosted_customer.Comments = address.get("comments")
        self.hosted_customer.URL = address.get("url")

    def purchase(self, money, credit_card, options={}):
        """Using Eway payment gateway , charge the given
        credit card for specified money"""
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        self.add_creditcard(credit_card)
        self.add_address(options)
        
        customer_id = self.client.create_hosted_customer(self.hosted_customer)
        pymt_response = self.client.process_payment(customer_id, 
                                                    money, 
                                                    options.get("invoice"),
                                                    options.get("description"))
        is_response = getattr(pymt_response, "CCPaymentResponse", None)
        if not is_response:
            transaction_was_unsuccessful.send(sender=self,
                                              type="purchase",
                                              response=pymt_response)
            return {"status": "FAILURE", "response": pymt_response}
        response = getattr(pymt_response, "CCPaymentResponse")
        transaction_was_successful.send(sender=self,
                                        type="purchase",
                                        response=response)
        return {"status": "SUCCESS", "response": response}
    
    def authorize(self, money, credit_card, options = {}):
        raise NotImplementedError

    def capture(self, money, authorization, options = {}):
        raise NotImplementedError

    def void(self, identification, options = {}):
        raise NotImplementedError

    def credit(self, money, identification, options = {}):
        raise NotImplementedError

    def recurring(self, money, creditcard, options = {}):
        raise NotImplementedError

    def store(self, creditcard, options = {}):
        raise NotImplementedError

    def unstore(self, identification, options = {}):
        raise NotImplementedError

