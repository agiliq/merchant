from django.conf import settings
from billing import CreditCard
from eway_api.client import RebillEwayClient
from billing import Gateway, GatewayNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful
from billing.utils.credit_card import Visa, MasterCard, DinersClub, JCB, AmericanExpress, InvalidCard

REBILL_TEST_URL = "https://www.eway.com.au/gateway/rebill/test/manageRebill_test.asmx?WSDL"
REBILL_LIVE_URL = "https://www.eway.com.au/gateway/rebill/manageRebill.asmx?WSDL"

HOSTED_TEST_URL = "https://www.eway.com.au/gateway/ManagedPaymentService/test/managedCreditCardPayment.asmx?WSDL"
HOSTED_LIVE_URL = "https://www.eway.com.au/gateway/ManagedPaymentService/managedCreditCardPayment.asmx?WSDL"

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
            self.customer_id = eway_settings['TEST_CUSTOMER_ID']
            self.rebill_url = REBILL_TEST_URL
            self.hosted_url = HOSTED_TEST_URL
        else:
            self.customer_id = eway_settings['CUSTOMER_ID']
            self.rebill_url = REBILL_LIVE_URL
            self.hosted_url = HOSTED_LIVE_URL
        
        self.eway_username = eway_settings['USERNAME']
        self.eway_password = eway_settings['PASSWORD']
        
        fp = open('/home/lalit/cred.txt', 'w+')
        fp.write(self.customer_id)
        fp.write(self.rebill_url)
        fp.write(self.hosted_url)
        fp.write(self.eway_username)
        fp.write(self.eway_password)
        fp.close()
            

    def add_creditcard(self, hosted_customer, credit_card):
        """add credit card details to the request parameters"""
        hosted_customer.CCNumber = credit_card.number
        hosted_customer.CCNameOnCard = credit_card.name
        hosted_customer.CCExpiryMonth = '%02d' % (credit_card.month)
        hosted_customer.CCExpiryYear = str(credit_card.year)[-2:]
        hosted_customer.FirstName = credit_card.first_name
        hosted_customer.LastName = credit_card.last_name

    def add_address(self, hosted_customer, options=None):
        """add address details to the request parameters"""
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
        """add customer details to the request parameters"""
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
        """add customer details to the request parameters"""
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
        
        client = RebillEwayClient(test_mode=self.test_mode,
                                      customer_id = self.customer_id,
                                      username = self.eway_username,
                                      password = self.eway_password,
                                      url=self.service_url,
                                      )
        hosted_customer = client.client.factory.create("CreditCard")
        
        self.add_creditcard(hosted_customer, credit_card)
        self.add_address(hosted_customer, options)
        customer_id = client.create_hosted_customer(hosted_customer)

        pymt_response = client.process_payment(customer_id,
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

    def authorize(self, money, credit_card, options=None):
        raise NotImplementedError

    def capture(self, money, authorization, options=None):
        raise NotImplementedError

    def void(self, identification, options=None):
        raise NotImplementedError

    def credit(self, money, identification, options=None):
        raise NotImplementedError

    def recurring(self, credit_card, options=None):
        """
            Recurring Payment Implementation using eWay recurring API (http://www.eway.com.au/developers/api/recurring)
            
            Input Parameters: 
                ( Please find the details here in this Gist: https://gist.github.com/df67e02f7ffb39f415e6 )
                credit_card   :    Customer Credit Card details ( Gist: )
                options       :    Customer and Recurring Payment details
            
            Output Dict:
                status: 'SUCCESS' or 'FAILURE'
                response : Response list of rebill event request in order of provided input 
                           in options["customer_rebill_details"] list.
        """
        if not options:
            options = {}
        '''
            # Validate Entered credit card details.
        '''
        if not self.validate_card(credit_card):
            raise InvalidCard("Invalid Card")
        
        rebillClient = RebillEwayClient(test_mode=self.test_mode,
                                  customer_id = self.customer_id,
                                  username = self.eway_username,
                                  password = self.eway_password,
                                  url=self.rebill_url,
                                  )
        # CustomerDetails : To create rebill Customer
        customer_detail = rebillClient.client.factory.create("CustomerDetails")
        self.add_customer_details(credit_card, customer_detail, options)
        '''
            # Create Rebill customer and retrieve customer rebill ID.
        '''
        rebill_customer_response = rebillClient.create_rebill_customer(customer_detail)
        
        # Handler error in create_rebill_customer response
        if rebill_customer_response.ErrorSeverity:
            transaction_was_unsuccessful.send(sender=self,
                                              type="recurringCreateRebill",
                                              response=rebill_customer_response)
            return {"status": "FAILURE", "response": rebill_customer_response}

        rebile_customer_id = rebill_customer_response.RebillCustomerID
        '''
            For Each rebill profile
            # Create Rebill events using rebill customer ID and customer rebill details.
        '''
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
                return {"status": "FAILURE", "response": rebill_event_response}

            rebill_event_response_list.append(rebill_event_response)
            
        transaction_was_successful.send(sender=self,
                                        type="recurring",
                                        response=rebill_event_response_list)
        
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
        rebillDeleteClient = RebillEwayClient(test_mode=self.test_mode,
                                  customer_id = self.customer_id,
                                  username = self.eway_username,
                                  password = self.eway_password,
                                  url=self.rebill_url,
                                  )

        '''
            # Delete Rebill Event, using customer create rebill detail.
        '''
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
    
    

def main():
    '''
        # Create recurring payment
    '''
#    options = {}
#    options["customer_details"] = {}
#    options["customer_details"]["customer_ref"] = 'REF1234'
#    options["customer_details"]["customer_salutation"] = "Mr./Ms."
#    options["customer_details"]["customer_company"] = ""
#    options["customer_details"]["customer_job_desc"] = ""
#    options["customer_details"]["customer_email"] = "test+eway@gmail.Com"
#    options["customer_details"]["customer_address1"] = ""
#    options["customer_details"]["customer_address2"] = ""
#    options["customer_details"]["customer_city"] = ""
#    options["customer_details"]["customer_state"] = ""
#    options["customer_details"]["customer_zip"] = ""
#    options["customer_details"]["customer_country"] = ""
#    options["customer_details"]["customer_phone1"] = "0297979797"
#    options["customer_details"]["customer_phone2"] = ""
#    options["customer_details"]["customer_fax"] = ""
#    options["customer_details"]["customer_url"] = "http://www.eway.Com.au"
#    options["customer_details"]["customer_comments"]= "Please Ship ASASP"
#    options["customer_rebill_details"] = []
#    rebill_details = {}
#    rebill_details["rebill_invRef"] = 'REF12345'
#    rebill_details["rebill_invDesc"] = "Monthly Recurring payment + Setup 299$"
#    rebill_details["rebill_initAmt"] = "29900"   # 299$
#    rebill_details["rebill_initDate"] = "04/01/2013"
#    rebill_details["rebill_recurAmt"] = "1000"   # 10$
#    rebill_details["rebill_startDate"] = "04/01/2013"
#    rebill_details["rebill_interval"] = "1"
#    rebill_details["rebill_intervalType"] = "3"
#    rebill_details["rebill_endDate"] = "03/04/2013"
#    options["customer_rebill_details"].append(rebill_details)
#    rebill_details = {}
#    rebill_details["rebill_invRef"] = 'REF12345'
#    rebill_details["rebill_invDesc"] = "Monthly Recurring payment 10$"
#    rebill_details["rebill_initAmt"] = "0"
#    rebill_details["rebill_initDate"] = "04/04/2013"
#    rebill_details["rebill_recurAmt"] = "1000"
#    rebill_details["rebill_startDate"] = "04/04/2013"
#    rebill_details["rebill_interval"] = "1"
#    rebill_details["rebill_intervalType"] = "3"
#    rebill_details["rebill_endDate"] = "03/04/2099"
#    options["customer_rebill_details"].append(rebill_details)
#
#    credit_card_data = {'first_name': 'testfname', 
#                        'last_name': 'testlname', 
#                        'verification_value': '123', 
#                        'number': '5105105105105100', 
#                        'month': '7', 
#                        'card_type': 'MasterCard', 
#                        'year': '2017'}
#    credit_card = CreditCard(**credit_card_data)
#    eWayGatewayObj = EwayGateway()
#    create_rebill_response = eWayGatewayObj.recurring(credit_card, options)
    '''
        # Cancel recurring payment
    '''
#    rebill_details = create_rebill_response['response']
#    print eWayGatewayObj.recurring_cancel(rebill_details.RebillCustomerID, rebill_details.RebillID)
        
if __name__ == '__main__':
    main()