import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from billing import CreditCard, get_gateway, get_integration
from billing.gateway import CardNotSupported

from app.forms import CreditCardForm
from django.conf import settings
from hashlib import md5

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
        form = CreditCardForm(initial={'number':'4222222222222'})
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
        form = CreditCardForm(initial={'number':'4797503429879309', 
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


def offsite_paypal(request):
    paypal_obj = get_integration("pay_pal")

    invoice_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return_url = request.build_absolute_uri(reverse('app_offsite_paypal_done'))
    cancel_return = request.build_absolute_uri(request.META['PATH_INFO'])
    notify_url = request.build_absolute_uri(reverse('paypal-ipn'))
    
    paypal_params = {'amount': 1,
                     'item_name': "name of the item",
                     'invoice': invoice_id,
                     'notify_url': notify_url,
                     'return_url': return_url,
                     'cancel_return': cancel_return,
                     }
    paypal_obj.add_fields(paypal_params)
    template_vars = {"obj": paypal_obj, 'title': 'PayPal Offsite'}
    return render(request, 'app/offsite_paypal.html', template_vars)

def offsite_google_checkout(request):
    gc = get_integration("google_checkout")
    return_url = request.build_absolute_uri(reverse('app_offsite_google_checkout_done'))
    fields = {'items': [{'amount': 1,
                         'name': 'name of the item',
                         'description': 'Item description',
                         'id': '999AXZ',
                         'currency': 'USD',
                         'quantity': 1,
                        }],
              'return_url': return_url,}
    gc.add_fields(fields)
    template_vars = {'title': 'Google Checkout', "gc_obj": gc}
    
    return render(request, 'app/google_checkout.html', template_vars)

def offsite_world_pay(request):
    wp = get_integration("world_pay")
    fields = {"instId": settings.WORLDPAY_INSTALLATION_ID_TEST,
              "cartId": "TEST123",
              "currency": "USD",
              "amount": 1,
              "desc": "Test Item",}
    wp.add_fields(fields)
    template_vars = {'title': 'WorldPay', "wp_obj": wp}
    return render(request, 'app/world_pay.html', template_vars)

def offsite_amazon_fps(request):
    fps = get_integration("amazon_fps")
    fields = {"transactionAmount": "100",
              "pipelineName": "SingleUse",
              "paymentReason": "Merchant Test",
              "paymentPage": request.build_absolute_uri(),
              "returnURLPrefix": "http://merchant.agiliq.com",
              }
    fps.add_fields(fields)
    # Save the fps.fields["callerReference"] in the db along with
    # the amount to be charged or use the user's unique id as
    # the callerReference so that the amount to be charged is known
    # Or save the callerReference in the session and send the user
    # to FPS and then use the session value when the user is back.
    fps_recur = get_integration("amazon_fps")
    fields = {"transactionAmount": "10",
              "pipelineName": "Recurring",
              "paymentReason": "Merchant",
              "paymentPage": request.build_absolute_uri(),
              "returnURLPrefix": "http://merchant.agiliq.com",
              "recurringPeriod": "1 Hour",
              }
    fps.add_fields(fields)
    template_vars = {'title': 'Amazon Flexible Payment Service', 
                     "fps_recur_obj": fps_recur, "fps_obj": fps}
    return render(request, 'app/amazon_fps.html', template_vars)
