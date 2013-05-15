import requests
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, tostring
from suds.client import Client, WebFault

from billing.utils.xml_parser import nodeToDic


# Token Payments urls( Web Service ) : http://www.eway.com.au/developers/api/token
HOSTED_TEST_URL = "https://www.eway.com.au/gateway/ManagedPaymentService/test/managedCreditCardPayment.asmx?WSDL"
HOSTED_LIVE_URL = "https://www.eway.com.au/gateway/ManagedPaymentService/managedCreditCardPayment.asmx?WSDL"

# Recurring Payments urls( Web Service ) : http://www.eway.com.au/developers/api/recurring
REBILL_TEST_URL = "https://www.eway.com.au/gateway/rebill/test/manageRebill_test.asmx?WSDL"
REBILL_LIVE_URL = "https://www.eway.com.au/gateway/rebill/manageRebill.asmx?WSDL"

# Direct Payments urls( XML Based ) : http://www.eway.com.au/developers/api/token
DIRECT_PAYMENT_TEST_URL = "https://www.eway.com.au/gateway_cvn/xmltest/testpage.asp"
DIRECT_PAYMENT_LIVE_URL = "https://www.eway.com.au/gateway_cvn/xmlpayment.asp"


class DirectPaymentClient(object):
    """
        Wrapper for eway payment gateway's Direct Payment:
            eWay Link: http://www.eway.com.au/developers/api/direct-payments

    """
    def __init__(self, gateway_url=None):
        self.gateway_url = gateway_url

    def process_direct_payment(self, direct_payment_details=None, **kwargs):
        """
            Eway Direct Payment API Url : http://www.eway.com.au/developers/api/direct-payments#tab-1
            Input and Output format: https://gist.github.com/2552fcaa2799045a7884
        """
        if direct_payment_details:
            # Create XML to send
            payment_xml_root = Element("ewaygateway")
            for each_field in direct_payment_details:
                field = Element(each_field)
                field.text = str(direct_payment_details.get(each_field))
                payment_xml_root.append(field)
            # pretty string
            payment_xml_string = tostring(payment_xml_root)
            response = requests.post(self.gateway_url, data=payment_xml_string)
            response_xml = parseString(response.text)
            response_dict = nodeToDic(response_xml)

            return response_dict
        else:
            return self.process_direct_payment(**kwargs)


class RebillEwayClient(object):
    """
        Wrapper for eway payment gateway's managed and rebill webservices

        To create a empty object from the webservice types, call self.client.factory.create('type_name')

        Useful types are
            CustomerDetails: rebill customer
            RebillEventDetails: rebill event
            CreditCard: hosted customer
    """

    def __init__(self, customer_id=None, username=None, password=None, url=None):
        self.gateway_url = url
        self.customer_id = customer_id
        self.username = username
        self.password = password
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
            eWay Urls : http://www.eway.com.au/developers/api/recurring
            Doc       : http://www.eway.com.au/docs/api-documentation/rebill-web-service.pdf?sfvrsn=2

            creates rebill customer with CustomerDetails type from the webservice

            also accepts keyword arguments if CustomerDetails object is not passed
            return CustomerDetails.RebillCustomerID and CustomerDetails.Result if successful
        """
        if rebill_customer:
            response = self.client.service.CreateRebillCustomer(
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
            return response
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
            eWay Urls : http://www.eway.com.au/developers/api/recurring
            Doc       : http://www.eway.com.au/docs/api-documentation/rebill-web-service.pdf?sfvrsn=2

            creates a rebill event based on RebillEventDetails object
            returns RebillEventDetails.RebillCustomerID and RebillEventDetails.RebillID if successful
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

    def delete_rebill_event(self, rebill_customer_id=None, rebill_event_id=None, **kwargs):
        """
            eWay Urls : http://www.eway.com.au/developers/api/recurring
            Doc       : http://www.eway.com.au/docs/api-documentation/rebill-web-service.pdf?sfvrsn=2

            Deletes a rebill event based on RebillEventDetails object
            returns Result as Successful if successful
        """
        if rebill_customer_id and rebill_event_id:
            return self.client.service.DeleteRebillEvent(rebill_customer_id, rebill_event_id)
        else:
            return self.client.service.DeleteRebillEvent(**kwargs)

    def update_rebill_event(self, **kwargs):
        """
            same as create, takes RebillEventDetails.RebillCustomerID and RebillEventDetails.RebillID
        """
        return self.client.service.CreateRebillEvent(**kwargs)

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
            eWay Urls : http://www.eway.com.au/developers/api/token
            Doc       : http://www.eway.com.au/docs/api-documentation/token-payments-field-description.pdf?sfvrsn=2

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
                    hosted_customer.Mobile,
                    hosted_customer.CustomerRef,
                    hosted_customer.JobDesc,
                    hosted_customer.Comments,
                    hosted_customer.URL,
                    hosted_customer.CCNumber,
                    hosted_customer.CCNameOnCard,
                    hosted_customer.CCExpiryMonth,
                    hosted_customer.CCExpiryYear,
                )
            else:
                return self.client.service.CreateCustomer(**kwargs)
        except WebFault as wf:
            print wf
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
