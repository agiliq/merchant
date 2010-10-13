
from django.conf import settings

from eway_api.client import RebillEwayClient, HOSTED_TEST_URL, HOSTED_LIVE_URL

TEST_URL     = 'https://www.eway.com.au/gateway/xmltest/testpage.asp'
LIVE_URL     = 'https://www.eway.com.au/gateway/xmlpayment.asp'

TEST_CVN_URL = 'https://www.eway.com.au/gateway_cvn/xmltest/testpage.asp'
LIVE_CVN_URL = 'https://www.eway.com.au/gateway_cvn/xmlpayment.asp'

class EwayGateway(object):
    def __init__(self):
        self.test_mode = getattr(settings, 'MERCHANT_TEST_MODE', True)
        self.client = RebillEwayClient(test_mode=self.test_mode,
                                      customer_id=settings.EWAY_CUSTOMER_ID,
                                      username=settings.EWAY_USERNAME,
                                      password=settings.EWAY_PASSWORD,
                                      url=HOSTED_TEST_URL if self.test_mode else HOSTED_LIVE_URL,
                                      )
        self.hosted_customer = self.client.client.factory.create("CreditCard")
    
    def purchase(self, money, credit_card, options={}):
        """Using Eway payment gateway , charge the given
        credit card for specified money"""
        self.add_creditcard(credit_card)
        self.add_address(options)
        
        customer_id = self.client.create_hosted_customer(self.hosted_customer)
        if self.test_mode:
            customer_id = '9876543211000'
        payment_result = self.client.process_payment(customer_id, 
                                                     money * 100, 
                                                     "test", 
                                                     "test")
        return payment_result
    
    def add_creditcard(self, credit_card):
        """add credit card details to the request parameters"""
        self.hosted_customer.CCNumber = credit_card.number
        self.hosted_customer.CCNameOnCard = "test"
        self.hosted_customer.CCExpiryMonth = '%02d' % (credit_card.month)
        self.hosted_customer.CCExpiryYear = str(credit_card.year)[-2:]
        self.hosted_customer.FirstName = credit_card.first_name
        self.hosted_customer.LastName = credit_card.last_name
    
    def add_address(self, options={}):
        """add address details to the request parameters"""
        self.hosted_customer.Title = "Mr."
        self.hosted_customer.Address = "test street"
        self.hosted_customer.Suburb = "Sydney"
        self.hosted_customer.State = "NSW"
        self.hosted_customer.Company = "Test Company"
        self.hosted_customer.PostCode = "2000"
        self.hosted_customer.Country = "au"
        self.hosted_customer.Email = "test@eway.com.au"
        self.hosted_customer.Fax = "0267720000"
        self.hosted_customer.Phone = "0267720000"
        self.hosted_customer.Mobile = "0404085992"
        self.hosted_customer.CustomerRef = "REF100"
        self.hosted_customer.JobDesc = "test"
        self.hosted_customer.Comments = "Now!"
        self.hosted_customer.URL = "http://www.google.com.au"
