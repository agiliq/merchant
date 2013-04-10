import unittest

from datetime import datetime, timedelta
from suds import WebFault

from client import RebillEwayClient, HOSTED_TEST_URL

# uncomment to enable debugging
#import logging
#logging.basicConfig(level=logging.DEBUG)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.rebill_test = RebillEwayClient(test_mode=True, customer_id='87654321', username='test@eway.com.au', password='test123')
        self.rebill_customer = self.rebill_test.client.factory.create("CustomerDetails")
        self.rebill_event = self.rebill_test.client.factory.create("RebillEventDetails")
        self.hosted_test = RebillEwayClient(test_mode=True,
                                            customer_id='87654321',
                                            username='test@eway.com.au',
                                            password='test123',
                                            url=HOSTED_TEST_URL)
        self.hosted_customer = self.hosted_test.client.factory.create("CreditCard")

        self.rebill_init_date = datetime.today()
        self.rebill_start_date = datetime.today() + timedelta(days=1)
        self.rebill_end_date = datetime.today() + timedelta(days=31)

    def test_create_rebill_customer(self):
        self.rebill_customer.CustomerTitle = "Mr."
        self.rebill_customer.CustomerFirstName = "Joe"
        self.rebill_customer.CustomerLastName = "Bloggs"
        self.rebill_customer.CustomerAddress = "test street"
        self.rebill_customer.CustomerSuburb = "Sydney"
        self.rebill_customer.CustomerState = "NSW"
        self.rebill_customer.CustomerCompany = "Test Company"
        self.rebill_customer.CustomerPostCode = "2000"
        self.rebill_customer.CustomerCountry = "au"
        self.rebill_customer.CustomerEmail = "test@eway.com.au"
        self.rebill_customer.CustomerFax = "0267720000"
        self.rebill_customer.CustomerPhone1 = "0267720000"
        self.rebill_customer.CustomerPhone2 = "0404085992"
        self.rebill_customer.CustomerRef = "REF100"
        self.rebill_customer.CustomerJobDesc = "test"
        self.rebill_customer.CustomerComments = "Now!"
        self.rebill_customer.CustomerURL = "http://www.google.com.au"

        new_rebill_customer = self.rebill_test.create_rebill_customer(self.rebill_customer)
        print "create rebill customer", new_rebill_customer
        self.assertEqual(new_rebill_customer.Result, "Success")

    def test_create_rebill_customer_with_kwargs(self):
        new_rebill_customer_with_kwargs = self.rebill_test.create_rebill_customer(
                                                                           customerTitle="Mr.",
                                                                           customerFirstName="Joe",
                                                                           customerLastName="Bloggs",
                                                                           customerAddress="test street",
                                                                           customerSuburb="Sydney",
                                                                           customerState="NSW",
                                                                           customerCompany="Test Company",
                                                                           customerPostCode="2000",
                                                                           customerCountry="au",
                                                                           customerEmail="test@eway.com.au",
                                                                           customerFax="0267720000",
                                                                           customerPhone1="0267720000",
                                                                           customerPhone2="0404085992",
                                                                           customerRef="REF100",
                                                                           customerJobDesc="test",
                                                                           customerURL="http://www.google.com.au",
                                                                           customerComments="Now!",
                                                                           )
        print "create rebill customer with kwargs", new_rebill_customer_with_kwargs
        self.assertEqual(new_rebill_customer_with_kwargs.Result, "Success")

    def test_update_rebill_customer(self):
        updated_rebill_customer = self.rebill_test.update_rebill_customer(
                                                                               RebillCustomerID="17609",
                                                                               customerTitle="Mr.",
                                                                               customerFirstName="Joe",
                                                                               customerLastName="Bloggs",
                                                                               customerAddress="test street",
                                                                               customerSuburb="Sydney",
                                                                               customerState="NSW",
                                                                               customerCompany="Test Company",
                                                                               customerPostCode="2000",
                                                                               customerCountry="au",
                                                                               customerEmail="test@eway.com.au",
                                                                               customerFax="0267720000",
                                                                               customerPhone1="0267720000",
                                                                               customerPhone2="0404085992",
                                                                               customerRef="REF100",
                                                                               customerJobDesc="test",
                                                                               customerURL="http://www.google.com.au",
                                                                               customerComments="Now!",
                                                                               )
        print "update rebill customer", updated_rebill_customer
        self.assertEqual(updated_rebill_customer.Result, "Success")

    def test_delete_rebill_customer(self):
        deleted_rebill_customer = self.rebill_test.delete_rebill_customer("10292")
        print "delete rebill customer", deleted_rebill_customer
        self.assertEqual(deleted_rebill_customer.Result, "Success")

    def test_create_rebill_event(self):
        self.rebill_event.RebillCustomerID = "60001545"
        self.rebill_event.RebillID = ""
        self.rebill_event.RebillInvRef = "ref123"
        self.rebill_event.RebillInvDesc = "test event"
        self.rebill_event.RebillCCName = "test"
        self.rebill_event.RebillCCNumber = "4444333322221111"
        self.rebill_event.RebillCCExpMonth = "07"
        self.rebill_event.RebillCCExpYear = "20"
        self.rebill_event.RebillInitAmt = "100"
        self.rebill_event.RebillInitDate = self.rebill_init_date.strftime("%d/%m/%Y")
        self.rebill_event.RebillRecurAmt = "100"
        self.rebill_event.RebillStartDate = self.rebill_init_date.strftime("%d/%m/%Y")
        self.rebill_event.RebillInterval = "1"
        self.rebill_event.RebillIntervalType = "1"
        self.rebill_event.RebillEndDate = self.rebill_end_date.strftime("%d/%m/%Y")

        new_rebill_event = self.rebill_test.create_rebill_event(self.rebill_event)
        print "create rebill event", new_rebill_event
        self.assertEqual(new_rebill_event.Result, "Success")

    def test_create_rebill_event_with_kwargs(self):
        new_rebill_event_with_kwargs = self.rebill_test.create_rebill_event(
                                                                                 RebillCustomerID="60001545",
                                                                                 RebillInvRef="ref123",
                                                                                 RebillInvDes="test",
                                                                                 RebillCCName="test",
                                                                                 RebillCCNumber="4444333322221111",
                                                                                 RebillCCExpMonth="07",
                                                                                 RebillCCExpYear="20",
                                                                                 RebillInitAmt="100",
                                                                                 RebillInitDate=self.rebill_init_date.strftime("%d/%m/%Y"),
                                                                                 RebillRecurAmt="100",
                                                                                 RebillStartDate=self.rebill_start_date.strftime("%d/%m/%Y"),
                                                                                 RebillInterval="1",
                                                                                 RebillIntervalType="1",
                                                                                 RebillEndDate=self.rebill_end_date.strftime("%d/%m/%Y")
                                                                                 )
        print "create rebill event with kwargs", new_rebill_event_with_kwargs
        self.assertEqual(new_rebill_event_with_kwargs.Result, "Success")

    def test_update_rebill_event(self):
        updated_rebill_event = self.rebill_test.update_rebill_event(
                                                                         RebillCustomerID="60001545",
                                                                         RebillID="80001208",
                                                                         RebillInvRef="ref123",
                                                                         RebillInvDes="test",
                                                                         RebillCCName="test",
                                                                         RebillCCNumber="4444333322221111",
                                                                         RebillCCExpMonth="07",
                                                                         RebillCCExpYear="20",
                                                                         RebillInitAmt="100",
                                                                         RebillInitDate=self.rebill_init_date.strftime("%d/%m/%Y"),
                                                                         RebillRecurAmt="100",
                                                                         RebillStartDate=self.rebill_start_date.strftime("%d/%m/%Y"),
                                                                         RebillInterval="1",
                                                                         RebillIntervalType="1",
                                                                         RebillEndDate=self.rebill_end_date.strftime("%d/%m/%Y")
                                                                         )
        print "update rebill event", updated_rebill_event
        self.assertEqual(updated_rebill_event.Result, "Success")

    def test_delete_rebill_event(self):
        deleted_rebill_event = self.rebill_test.delete_rebill_event("10292", "80001208")
        print "delete rebill event", deleted_rebill_event
        self.assertEqual(deleted_rebill_event.Result, "Success")

    def test_query_next_transaction(self):
        query_next_transaction_result = self.rebill_test.query_next_transaction("60001545", "80001227")
        print "test_query_next_transaction", query_next_transaction_result
        self.assertFalse(query_next_transaction_result == None)

    def test_query_rebill_customer(self):
        query_rebill_customer_result = self.rebill_test.query_rebill_customer("60001545")
        print "test_query_rebill_customer", query_rebill_customer_result
        self.assertFalse(query_rebill_customer_result == None)

    def test_query_rebill_event(self):
        query_rebill_result = self.rebill_test.query_rebill_event("60001545", "80001227")
        print "test_query_rebill_event", query_rebill_result
        self.assertFalse(query_rebill_result == None)

    def test_query_transactions(self):
        query_transactions_result = self.rebill_test.query_transactions("60001545", "80001208")
        print "test_query_transactions", query_transactions_result
        self.assertFalse(query_transactions_result == None)

    def test_create_hosted_customer(self):
        self.hosted_customer.Title = "Mr."
        self.hosted_customer.FirstName = "Joe"
        self.hosted_customer.LastName = "Bloggs"
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
        self.hosted_customer.CCNumber = "4444333322221111"
        self.hosted_customer.CCNameOnCard = "test"
        self.hosted_customer.CCExpiryMonth = "07"
        self.hosted_customer.CCExpiryYear = "12"

        new_hosted_customer_id = self.hosted_test.create_hosted_customer(self.hosted_customer)
        print "create new hosted customer", new_hosted_customer_id
        self.assertFalse(isinstance(new_hosted_customer_id, WebFault))

    def test_create_hosted_customer_with_kwargs(self):
        new_hosted_customer_id = self.hosted_test.create_hosted_customer(
                                                                          Title="Mr.",
                                                                          FirstName="Joe",
                                                                          LastName="Bloggs",
                                                                          Address="test street",
                                                                          Suburb="Sydney",
                                                                          State="NSW",
                                                                          Company="Test Company",
                                                                          PostCode="2000",
                                                                          Country="au",
                                                                          Email="test@eway.com.au",
                                                                          Fax="0267720000",
                                                                          Phone="0267720000",
                                                                          Mobile="0404085992",
                                                                          CustomerRef="REF100",
                                                                          JobDesc="test",
                                                                          Comments="Now!",
                                                                          URL="http://www.google.com.au",
                                                                          CCNumber="4444333322221111",
                                                                          CCNameOnCard="test",
                                                                          CCExpiryMonth="07",
                                                                          CCExpiryYear="12"
                                                                          )
        print "create new hosted customer with kwargs", new_hosted_customer_id
        self.assertFalse(isinstance(new_hosted_customer_id, WebFault))

    def test_update_hosted_customer(self):
        updated_hosted_customer = self.hosted_test.update_hosted_customer(
                                                                          managedCustomerID="9876543211000",
                                                                          Title="Mr.",
                                                                          FirstName="Joe",
                                                                          LastName="Bloggs",
                                                                          Address="test street",
                                                                          Suburb="Sydney",
                                                                          State="NSW",
                                                                          Company="Test Company",
                                                                          PostCode="2000",
                                                                          Country="au",
                                                                          Email="test@eway.com.au",
                                                                          Fax="0267720000",
                                                                          Phone="0267720000",
                                                                          Mobile="0404085992",
                                                                          CustomerRef="REF100",
                                                                          JobDesc="test",
                                                                          Comments="Now!",
                                                                          URL="http://www.google.com.au",
                                                                          CCNumber="4444333322221111",
                                                                          CCNameOnCard="test",
                                                                          CCExpiryMonth="07",
                                                                          CCExpiryYear="12"
                                                                          )
        print "update hosted customer", updated_hosted_customer
        self.assertTrue(updated_hosted_customer)

    def test_process_payment(self):
        payment_result = self.hosted_test.process_payment("9876543211000", "100", "test", "test")
        print "test_process_payment", payment_result
        self.assertFalse(isinstance(payment_result, WebFault))

    def test_query_customer(self):
        query_result = self.hosted_test.query_customer("9876543211000")
        print "test_query_customer", query_result
        self.assertFalse(query_result == None)

    def test_query_payment(self):
        query_payment_result = self.hosted_test.query_payment("9876543211000")
        print "test_query_payment", query_payment_result
        self.assertFalse(query_payment_result == None)

if __name__ == '__main__':
    unittest.main()
