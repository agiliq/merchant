from suds.client import Client, WebFault

REBILL_TEST_URL = "https://www.eway.com.au/gateway/rebill/test/manageRebill_test.asmx?WSDL"
REBILL_LIVE_URL = "https://www.eway.com.au/gateway/rebill/manageRebill.asmx?WSDL"

HOSTED_TEST_URL = "https://www.eway.com.au/gateway/ManagedPaymentService/test/managedCreditCardPayment.asmx?WSDL"
HOSTED_LIVE_URL = "https://www.eway.com.au/gateway/ManagedPaymentService/managedCreditCardPayment.asmx?WSDL"

class RebillEwayClient(object):
    """
    Wrapper for eway payment gateway's managed and rebill webservices
    
    To create a empty object from the webservice types, call self.client.factory.create('type_name')
    
    Useful types are 
        CustomerDetails: rebill customer
        RebillEventDetails: rebill event
        CreditCard: hosted customer
    """
    def __init__(self, test_mode=True, customer_id=None, username=None, password=None, url=None):
        self.gateway_url = REBILL_LIVE_URL
        self.test_mode = test_mode
        self.customer_id = customer_id
        self.username = username
        self.password = password
        if test_mode:
            self.gateway_url = REBILL_TEST_URL
        if url:
            self.gateway_url = url
        self.client = Client(self.gateway_url)
        self.set_eway_header()
        
    def set_eway_header(self):
        """
        creates eway header containing login credentials
        
        required for all api calls
        """
        eway_header = self.client.factory.create("eWAYHeader")
        eway_header.eWAYCustomerID = self.customer_id
        eway_header.Username = self.username
        eway_header.Password = self.password
        self.client.set_options(soapheaders=eway_header)
        
    def create_rebill_customer(self, rebill_customer=None, **kwargs):
        """
        creates rebill customer with CustomerDetails type from the webservice
        
        also accepts keyword arguments if CustomerDetails object is not passed
        return CustomerDetails.RebillCustomerID and CustomerDetails.Result if successfull
        """
        if rebill_customer:
            return self.client.service.CreateRebillCustomer(
                                                             rebill_customer.CustomerTitle,
                                                             rebill_customer.CustomerFirstName,
                                                             rebill_customer.CustomerLastName,
                                                             rebill_customer.CustomerAddress,
                                                             rebill_customer.CustomerSuburb,
                                                             rebill_customer.CustomerState,
                                                             rebill_customer.CustomerCompany,
                                                             rebill_customer.CustomerPostCode,
                                                             rebill_customer.CustomerCountry,
                                                             rebill_customer.CustomerEmail,
                                                             rebill_customer.CustomerFax,
                                                             rebill_customer.CustomerPhone1,
                                                             rebill_customer.CustomerPhone2,
                                                             rebill_customer.CustomerRef,
                                                             rebill_customer.CustomerJobDesc,
                                                             rebill_customer.CustomerComments,
                                                             rebill_customer.CustomerURL,
                                                             )
        else:
            return self.client.service.CreateRebillCustomer(**kwargs)
    
    def update_rebill_customer(self, **kwargs):
        """
        same as create, takes CustomerDetails.RebillCustomerID
        """
        return self.client.service.UpdateRebillCustomer(**kwargs)

    def delete_rebill_customer(self, rebill_customer_id):
        """
        deletes a rebill customer based on id
        """ 
        return self.client.service.DeleteRebillCustomer(rebill_customer_id)
         
    
    def create_rebill_event(self, rebill_event=None, **kwargs):
        """
        creates a rebill event based on RebillEventDetails object
        returns RebillEventDetails.RebillCustomerID and RebillEventDetails.RebillID if successfull
        """
        if rebill_event:
            return self.client.service.CreateRebillEvent(
                                                            rebill_event.RebillCustomerID,
                                                            rebill_event.RebillInvRef,
                                                            rebill_event.RebillInvDesc,
                                                            rebill_event.RebillCCName,
                                                            rebill_event.RebillCCNumber,
                                                            rebill_event.RebillCCExpMonth,
                                                            rebill_event.RebillCCExpYear,
                                                            rebill_event.RebillInitAmt,
                                                            rebill_event.RebillInitDate,
                                                            rebill_event.RebillRecurAmt,
                                                            rebill_event.RebillStartDate,
                                                            rebill_event.RebillInterval,
                                                            rebill_event.RebillIntervalType,
                                                            rebill_event.RebillEndDate,
                                                           )
        else:
            return self.client.service.CreateRebillEvent(**kwargs)

    def update_rebill_event(self, **kwargs):
        """
        same as create, takes RebillEventDetails.RebillCustomerID and RebillEventDetails.RebillID
        """
        return self.client.service.CreateRebillEvent(**kwargs)

    def delete_rebill_event(self, rebill_customer_id, rebill_event_id):
        """
        delete a rebill event based on rebill customer id and event id
        """
        return self.client.service.DeleteRebillEvent(rebill_customer_id, rebill_event_id)
    
    def query_next_transaction(self, RebillCustomerID, RebillID):
        return self.client.service.QueryNextTransaction(RebillCustomerID, RebillID)
    
    def query_rebill_customer(self, RebillCustomerID):
        return self.client.service.QueryRebillCustomer(RebillCustomerID)
    
    def query_rebill_event(self, RebillCustomerID, RebillID):
        return self.client.service.QueryRebillEvent(RebillCustomerID, RebillID)        
    
    def query_transactions(self, RebillCustomerID, RebillID, startDate=None, endDate=None, status=None):
        try:
            return self.client.service.QueryTransactions(RebillCustomerID, RebillID, startDate, endDate, status)
        except WebFault as wf:
            return wf
    
    def create_hosted_customer(self, hosted_customer=None, **kwargs):
        """
        creates hosted customer based on CreditCard type details or kwargs
        
        returns id of newly created customer (112233445566 in test mode) 
        """
        try:
            if hosted_customer:
                return self.client.service.CreateCustomer(
                                                            hosted_customer.Title,
                                                            hosted_customer.FirstName,
                                                            hosted_customer.LastName,
                                                            hosted_customer.Address,
                                                            hosted_customer.Suburb,
                                                            hosted_customer.State,
                                                            hosted_customer.Company,
                                                            hosted_customer.PostCode,
                                                            hosted_customer.Country,
                                                            hosted_customer.Email,
                                                            hosted_customer.Fax,
                                                            hosted_customer.Phone,
                                                            # hosted_customer.Mobile,
                                                            # hosted_customer.CustomerRef,
                                                            # hosted_customer.JobDesc,
                                                            # hosted_customer.Comments,
                                                            # hosted_customer.URL,
                                                            hosted_customer.CCNumber,
                                                            hosted_customer.CCNameOnCard,
                                                            hosted_customer.CCExpiryMonth,
                                                            hosted_customer.CCExpiryYear,
                                                            )
            else:
                return self.client.service.CreateCustomer(**kwargs)
        except WebFault as wf:
            return wf
    
    def update_hosted_customer(self, **kwargs):
        """
        Update hosted customer based on kwargs
        
        returns True or False
        """
        try:
            return self.client.service.UpdateCustomer(**kwargs)
        except WebFault as wf:
            return wf        
    
    def process_payment(self, managedCustomerID, amount, invoiceReference, invoiceDescription):
        """
        makes a transaction based on customer id and amount
        
        returns CCPaymentResponse type object with ewayTrxnStatus, ewayTrxnNumber, ewayAuthCode
        """
        try:
            return self.client.service.ProcessPayment(managedCustomerID, amount, invoiceReference, invoiceDescription)
        except WebFault as wf:
            return wf
    
    def query_customer(self, managedCustomerID):
        return self.client.service.QueryCustomer(managedCustomerID)
    
    def query_customer_by_reference(self, CustomerReference):
        """
        returns customer details based on reference
        
        not working with test data
        """
        return self.client.service.QueryCustomerByReference(CustomerReference)
    
    def query_payment(self, managedCustomerID):
        return self.client.service.QueryPayment(managedCustomerID)
