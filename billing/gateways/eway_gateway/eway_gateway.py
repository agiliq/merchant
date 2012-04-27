
from django.conf import settings
from eway_api.client import RebillEwayClient, HOSTED_TEST_URL, HOSTED_LIVE_URL
from billing import Gateway, GatewayNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import Visa, MasterCard, DinersClub, JCB, AmericanExpress

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
        if self.test_mode:
            customer_id = eway_settings['TEST_CUSTOMER_ID']
        else:
            customer_id = eway_settings['CUSTOMER_ID']
        self.client = RebillEwayClient(test_mode=self.test_mode,
                                      customer_id=customer_id,
                                      username=eway_settings['USERNAME'],
                                      password=eway_settings['PASSWORD'],
                                      url=self.service_url,
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
    
    def add_address(self, options=None):
        """add address details to the request parameters"""
        if not options:
            options = {}
        address = options.get("billing_address", {})
        self.hosted_customer.Title = address.get("salutation", "Mr./Ms.")
        self.hosted_customer.Address = address.get("address1", '') + address.get("address2", "")
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

    @property
    def service_url(self):
        if self.test_mode:
            return HOSTED_TEST_URL
        return HOSTED_LIVE_URL

    def purchase(self, money, credit_card, options=None):
        """Using Eway payment gateway , charge the given
        credit card for specified money"""
        if not options:
            options = {}
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        self.add_creditcard(credit_card)
        self.add_address(options)
        
        customer_id = self.client.create_hosted_customer(self.hosted_customer)
        pymt_response = self.client.process_payment(customer_id, 
                                                    money, 
                                                    options.get("invoice", 'test'),
                                                    options.get("description", 'test'))
        
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
    
    def authorize(self, money, credit_card, options = None):
        raise NotImplementedError

    def capture(self, money, authorization, options = None):
        raise NotImplementedError

    def void(self, identification, options = None):
        raise NotImplementedError

    def credit(self, money, identification, options = None):
        raise NotImplementedError

    def recurring(self, money, creditcard, options = None):
        raise NotImplementedError

    def store(self, creditcard, options = None):
        raise NotImplementedError

    def unstore(self, identification, options = None):
        raise NotImplementedError

