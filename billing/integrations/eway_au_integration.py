from billing import Integration, get_gateway, IntegrationNotConfigured
from billing.forms.eway_au_forms import EwayAuForm
from django.conf import settings
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
import operator
from suds.client import Client


client = Client("https://au.ewaygateway.com/mh/soap.asmx?wsdl")
client.options.cache.setduration(days=7)


translation = {
    'SaveToken': 'save_token',
    'TokenCustomerID': 'token_customer_id',
    'Reference': 'reference',
    'Title': 'title',
    'FirstName': 'first_name',
    'LastName': 'last_name',
    'CompanyName': 'company',
    'JobDescription': 'job',
    'Street1': 'street',
    'City': 'city',
    'State': 'state',
    'PostalCode': 'postal_code',
    'Country': 'country',
    'Email': 'email',
    'Phone': 'phone',
    'Mobile': 'mobile',
    'Comments': 'comments',
    'Fax': 'fax',
    'Url': 'url',
    'CardNumber': 'card_number',
    'CardName': 'card_name',
    'CardExpiryMonth': 'card_expiry_month',
    'CardExpiryYear': 'card_expiry_year',
    'Option1': 'option_1',
    'Option2': 'option_2',
    'Option3': 'option_3',
    'BeagleScore': 'beagle_score',
    'ErrorMessage': 'error_message',
    'TransactionStatus': 'transaction_status',
    'TransactionID': 'transaction_id',
    'TotalAmount': 'total_amount',
    'InvoiceReference': 'invoice_reference',
    'InvoiceNumber': 'invoice_number',
    'ResponseCode': 'response_code',
    'ResponseMessage': 'response_message',
    'AuthorisationCode': 'authorisation_code',
    'AccessCode': 'access_code',
}
translation.update(dict(zip(translation.values(), translation.keys())))


def translate(original):
    """
    Translate between the eWAY SOAP naming convention (camel case), and
    Python's convention (lowercase separated with underscores).

    Takes and returns a dictionary.

    Untranslatable keys are not included in returned dict.
    """
    translated = {}
    for k, v in translation.items():
        try:
            value = original[k]
        except KeyError:
            continue
        translated[v] = value
    return translated


def attr_update(object_, dict_):
    for k, v in dict_.items():
        setattr(object_, k, v)


class EwayAuIntegration(Integration):
    display_name = "eWAY"
    service_url = "https://au.ewaygateway.com/mh/payment"
    template = "billing/eway.html"
    urls = ()

    def __init__(self, access_code=None):
        super(EwayAuIntegration, self).__init__()
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("eway"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                           "configured." % self.display_name)
        eway_settings = merchant_settings["eway"]
        self.customer_id = eway_settings["CUSTOMER_ID"]
        self.username = eway_settings["USERNAME"]
        self.password = eway_settings["PASSWORD"]
        # Don't use X-Forwarded-For. It doesn't really matter if REMOTE_ADDR
        # isn't their *real* IP, we're only interested in what IP they're going
        # to use for their POST request to eWAY. If they're using a proxy to
        # connect to us, it's fair to assume they'll use the same proxy to
        # connect to eWAY.
        self.access_code = access_code

    def generate_form(self):
        initial_data = dict(EWAY_ACCESSCODE=self.access_code, **self.fields)
        return EwayAuForm(initial=initial_data)

    def request_access_code(self, payment, return_url, customer=None,
                            billing_country=None, ip_address=None):
        # enforce required fields
        assert self.customer_id
        assert self.username
        assert self.password
        assert payment['total_amount']
        assert return_url

        # Request a new access code.
        req = client.factory.create("CreateAccessCodeRequest")
        req.Authentication.CustomerID = self.customer_id
        req.Authentication.Username = self.username
        req.Authentication.Password = self.password
        attr_update(req.Payment, translate(payment))
        attr_update(req.Customer, translate(customer or {}))
        req.RedirectUrl = return_url
        if ip_address:
            req.IPAddress = ip_address
        if billing_country:
            req.BillingCountry = billing_country
        del req.ResponseMode

        # Handle the response
        response = client.service.CreateAccessCode(req)
        self.access_code = response.AccessCode

        # turn customer to dict
        customer_echo = dict(((k, getattr(response.Customer, k))
                              for k in dir(response.Customer)))
        return (self.access_code, translate(customer_echo))

    def check_transaction(self):
        if not self.access_code:
            raise ValueError("`access_code` must be specified")

        req = client.factory.create("GetAccessCodeResultRequest")
        req.Authentication.CustomerID = self.customer_id
        req.Authentication.Username = self.username
        req.Authentication.Password = self.password
        req.AccessCode = self.access_code

        response = client.service.GetAccessCodeResult(req)
        return translate(dict(((k, getattr(response, k)) for k in dir(response))))
