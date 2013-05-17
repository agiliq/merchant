import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect  # , HttpResponse

from billing import CreditCard, get_gateway, get_integration
from billing.gateway import CardNotSupported

from app.forms import CreditCardForm
from app.urls import (authorize_net_obj, google_checkout_obj, world_pay_obj, pay_pal_obj,
                      amazon_fps_obj, fps_recur_obj, braintree_obj,
                      stripe_obj, ogone_obj)
from django.conf import settings
from django.contrib.sites.models import RequestSite
from billing.utils.paylane import PaylanePaymentCustomer, \
    PaylanePaymentCustomerAddress

def render(request, template, template_vars={}):
    return render_to_response(template, template_vars, RequestContext(request))

def index(request, gateway=None):
    return authorize(request)

def authorize(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("authorize_net")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            response = merchant.purchase(amount, credit_card)
            #response = merchant.recurring(amount, credit_card)
    else:
        form = CreditCardForm(initial={'number': '4222222222222'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Authorize'})


def paypal(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("pay_pal")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            # response = merchant.purchase(amount, credit_card, options={'request': request})
            response = merchant.recurring(amount, credit_card, options={'request': request})
    else:
        form = CreditCardForm(initial={'number': '4797503429879309',
                                       'verification_value': '037',
                                       'month': 1,
                                       'year': 2019,
                                       'card_type': 'visa'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Paypal'})


def eway(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("eway")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            billing_address = {'salutation': 'Mr.',
                               'address1': 'test',
                               'address2': ' street',
                               'city': 'Sydney',
                               'state': 'NSW',
                               'company': 'Test Company',
                               'zip': '2000',
                               'country': 'au',
                               'email': 'test@example.com',
                               'fax': '0267720000',
                               'phone': '0267720000',
                               'mobile': '0404085992',
                               'customer_ref': 'REF100',
                               'job_desc': 'test',
                               'comments': 'any',
                               'url': 'http://www.google.com.au',
                               }
            response = merchant.purchase(amount, credit_card, options={'request': request, 'billing_address': billing_address})
    else:
        form = CreditCardForm(initial={'number':'4444333322221111',
                                       'verification_value': '000',
                                       'month': 7,
                                       'year': 2012})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Eway'})

def braintree(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("braintree_payments")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            response = merchant.purchase(amount, credit_card)
    else:
        form = CreditCardForm(initial={'number':'4111111111111111'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Braintree Payments (S2S)'})
def stripe(request):
    amount = 1
    response= None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("stripe")
            response = merchant.purchase(amount,credit_card)
    else:
        form = CreditCardForm(initial={'number':'4242424242424242'})
    return render(request, 'app/index.html',{'form': form,
                                             'amount':amount,
                                             'response':response,
                                             'title':'Stripe Payment'})


def paylane(request):
    amount = 1
    response= None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("paylane")
            customer = PaylanePaymentCustomer()
            customer.name = "%s %s" %(data['first_name'], data['last_name'])
            customer.email = "testuser@example.com"
            customer.ip_address = "127.0.0.1"
            options = {}
            address = PaylanePaymentCustomerAddress()
            address.street_house = 'Av. 24 de Julho, 1117'
            address.city = 'Lisbon'
            address.zip_code = '1700-000'
            address.country_code = 'PT'
            customer.address = address
            options['customer'] = customer
            options['product'] = {}
            response = merchant.purchase(amount, credit_card, options = options)
    else:
        form = CreditCardForm(initial={'number':'4111111111111111'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount':amount,
                                              'response':response,
                                              'title':'Paylane Gateway'})


def we_pay(request):
    wp = get_gateway("we_pay")
    form = None
    amount = 10
    response = wp.purchase(10, None, {
            "description": "Test Merchant Description",
            "type": "SERVICE",
            "redirect_uri": request.build_absolute_uri(reverse('app_we_pay_redirect'))
            })
    if response["status"] == "SUCCESS":
        return HttpResponseRedirect(response["response"]["checkout_uri"])
    return render(request, 'app/index.html', {'form': form,
                                              'amount':amount,
                                              'response':response,
                                              'title':'WePay Payment'})

def we_pay_redirect(request):
    checkout_id = request.GET.get("checkout_id", None)
    return render(request, 'app/we_pay_success.html', {"checkout_id": checkout_id})


def we_pay_ipn(request):
    # Just a dummy view for now.
    return render(request, 'app/index.html', {})


def beanstream(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("beanstream")
            response = merchant.purchase(amount, credit_card,
                                         {"billing_address": {
                        "name": "%s %s" % (data["first_name"], data["last_name"]),
                        # below are hardcoded just for the sake of the example
                        # you can make these optional by toggling the customer name
                        # and address in the account dashboard.
                        "email": "test@example.com",
                        "phone": "555-555-555-555",
                        "address1": "Addr1",
                        "address2": "Addr2",
                        "city": "Hyd",
                        "state": "AP",
                        "country": "IN"
                        }
                                          })
    else:
        form = CreditCardForm(initial={'number':'4030000010001234',
                                       'card_type': 'visa',
                                       'verification_value': 123})
    return render(request, 'app/index.html',{'form': form,
                                             'amount': amount,
                                             'response': response,
                                             'title': 'Beanstream'})

def chargebee(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("chargebee")
            response = merchant.purchase(amount, credit_card,
                                         {"plan_id": "professional",
                                          "description": "Quick Purchase"})
    else:
        form = CreditCardForm(initial={'number':'4111111111111111',
                                       'card_type': 'visa',
                                       'verification_value': 100})
    return render(request, 'app/index.html',{'form': form,
                                             'amount': amount,
                                             'response': response,
                                             'title': 'Chargebee'})

def offsite_authorize_net(request):
    params = {'x_amount': 1,
              'x_fp_sequence': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
              'x_fp_timestamp': datetime.datetime.now().strftime('%s'),
              'x_recurring_bill': 'F',
              }
    authorize_net_obj.add_fields(params)
    template_vars = {"obj": authorize_net_obj, 'title': authorize_net_obj.display_name}
    return render(request, 'app/offsite_authorize_net.html', template_vars)


def offsite_paypal(request):
    invoice_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return_url = request.build_absolute_uri(reverse('app_offsite_paypal_done'))
    cancel_return = request.build_absolute_uri(request.META['PATH_INFO'])
    notify_url = request.build_absolute_uri(reverse('paypal-ipn'))

    paypal_params = {
        'amount_1': 1,
        'item_name_1': "Item 1",
        'amount_2': 2,
        'item_name_2': "Item 2",
        'invoice': invoice_id,
        'notify_url': notify_url,
        'return_url': return_url,
        'cancel_return': cancel_return,
    }
    pay_pal_obj.add_fields(paypal_params)
    template_vars = {"obj": pay_pal_obj, 'title': 'PayPal Offsite'}
    return render(request, 'app/offsite_paypal.html', template_vars)

def offsite_google_checkout(request):
    return_url = request.build_absolute_uri(reverse('app_offsite_google_checkout_done'))
    fields = {
            'items': [{
                'amount': 1,
                'name': 'name of the item',
                'description': 'Item description',
                'id': '999AXZ',
                'currency': 'USD',
                'quantity': 1,
                "subscription": {
                "type": "merchant",                     # valid choices is ["merchant", "google"]
                "period": "YEARLY",                     # valid choices is ["DAILY", "WEEKLY", "SEMI_MONTHLY", "MONTHLY", "EVERY_TWO_MONTHS"," QUARTERLY", "YEARLY"]
                "payments": [{
                        "maximum-charge": 9.99,         # Item amount must be "0.00"
                        "currency": "USD"
                }]
            },
            "digital-content": {
                "display-disposition": "OPTIMISTIC",    # valid choices is ['OPTIMISTIC', 'PESSIMISTIC']
                "description": "Congratulations! Your subscription is being set up. Continue: {return_url}".format(return_url=return_url)
            },
        }],
        'return_url': return_url
    }
    google_checkout_obj.add_fields(fields)
    template_vars = {'title': 'Google Checkout', "gc_obj": google_checkout_obj}

    return render(request, 'app/google_checkout.html', template_vars)

def offsite_world_pay(request):
    fields = {"instId": settings.MERCHANT_SETTINGS["world_pay"]["INSTALLATION_ID_TEST"],
              "cartId": "TEST123",
              "currency": "USD",
              "amount": 1,
              "desc": "Test Item",}
    world_pay_obj.add_fields(fields)
    template_vars = {'title': 'WorldPay', "wp_obj": world_pay_obj}
    return render(request, 'app/world_pay.html', template_vars)

def offsite_amazon_fps(request):
    url_scheme = "http"
    if request.is_secure():
        url_scheme = "https"
    fields = {"transactionAmount": "100",
              "pipelineName": "SingleUse",
              "paymentReason": "Merchant Test",
              "paymentPage": request.build_absolute_uri(),
              "returnURL": "%s://%s%s" % (url_scheme,
                                          RequestSite(request).domain,
                                          reverse("fps_return_url"))
              }
    # Save the fps.fields["callerReference"] in the db along with
    # the amount to be charged or use the user's unique id as
    # the callerReference so that the amount to be charged is known
    # Or save the callerReference in the session and send the user
    # to FPS and then use the session value when the user is back.
    amazon_fps_obj.add_fields(fields)
    fields.update({"transactionAmount": "100",
                   "pipelineName": "Recurring",
                   "recurringPeriod": "1 Hour",
                   })
    fps_recur_obj.add_fields(fields)
    template_vars = {'title': 'Amazon Flexible Payment Service',
                     "fps_recur_obj": fps_recur_obj,
                     "fps_obj": amazon_fps_obj}
    return render(request, 'app/amazon_fps.html', template_vars)

def offsite_braintree(request):
    fields = {"transaction": {
            "order_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "type": "sale",
            "options": {
                "submit_for_settlement": True
                },
            },
            "site": "%s://%s" % ("https" if request.is_secure() else "http",
                                RequestSite(request).domain)
            }
    braintree_obj.add_fields(fields)
    template_vars = {'title': 'Braintree Payments Transparent Redirect',
                     "bp_obj": braintree_obj}
    return render(request, "app/braintree_tr.html", template_vars)

def offsite_stripe(request):
    status = request.GET.get("status")
    stripe_obj.add_field("amount", 100)
    template_vars = {'title': 'Stripe.js',
                     "stripe_obj": stripe_obj,
                     "status": status}
    return render(request, "app/stripe.html", template_vars)


def offsite_eway(request):
    return_url = request.build_absolute_uri(reverse(offsite_eway_done))
    eway_obj = get_integration("eway_au")
    customer = eway_obj.request_access_code(
            return_url=return_url, customer={},
            payment={"total_amount": 100})
    request.session["eway_access_code"] = eway_obj.access_code
    template_vars = {"title": "eWAY",
                     "eway_obj": eway_obj}
    return render(request, "app/eway.html", template_vars)


def offsite_eway_done(request):
    access_code = request.session["eway_access_code"]
    eway_obj = get_integration("eway_au", access_code=access_code)
    result = eway_obj.check_transaction()

    return render(request, "app/eway_done.html", {"result": result})


def bitcoin(request):
    amount = 0.01
    bitcoin_obj = get_gateway("bitcoin")
    address = request.session.get("bitcoin_address", None)
    if not address:
        address = bitcoin_obj.get_new_address()
        request.session["bitcoin_address"] = address
    return render(request, "app/bitcoin.html", {
        "title": "Bitcoin",
        "amount": amount,
        "address": address
    })

def bitcoin_done(request):
    amount = 0.01
    bitcoin_obj = get_gateway("bitcoin")
    address = request.session.get("bitcoin_address", None)
    if not address:
        return HttpResponseRedirect(reverse("app_bitcoin"))
    result = bitcoin_obj.purchase(amount, address)
    if result['status'] == 'SUCCESS':
        del request.session["bitcoin_address"]
    return render(request, "app/bitcoin_done.html", {
        "title": "Bitcoin",
        "amount": amount,
        "address": address,
        "result": result
    })


def offsite_ogone(request):
    from utils import randomword
    fields = {
        # Required
        # orderID needs to be unique per transaction.
        'orderID': randomword(6),
        'currency': u'INR',
        'amount': u'10000',  # 100.00
        'language': 'en_US',

        # Optional; Can be configured in Ogone Account:

        'exceptionurl': request.build_absolute_uri(reverse("ogone_notify_handler")),
        'declineurl': request.build_absolute_uri(reverse("ogone_notify_handler")),
        'cancelurl': request.build_absolute_uri(reverse("ogone_notify_handler")),
        'accepturl': request.build_absolute_uri(reverse("ogone_notify_handler")),

        # Optional fields which can be used for billing:

        # 'homeurl': u'http://127.0.0.1:8000/',
        # 'catalogurl': u'http://127.0.0.1:8000/',
        # 'ownerstate': u'',
        # 'cn': u'Venkata Ramana',
        # 'ownertown': u'Hyderabad',
        # 'ownercty': u'IN',
        # 'ownerzip': u'Postcode',
        # 'owneraddress': u'Near Madapur PS',
        # 'com': u'Order #21: Venkata Ramana',
        # 'email': u'ramana@agiliq.com'
    }
    ogone_obj.add_fields(fields)
    return render(request, "app/ogone.html", {"og_obj": ogone_obj})
