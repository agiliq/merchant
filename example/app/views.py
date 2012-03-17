import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from billing import CreditCard, get_gateway
from billing.gateway import CardNotSupported

from app.forms import CreditCardForm
from app.urls import (google_checkout_obj, world_pay_obj,
                      pay_pal_obj, amazon_fps_obj,
                      fps_recur_obj, braintree_obj,
                      stripe_obj,samurai_obj)
from django.conf import settings
from django.contrib.sites.models import RequestSite

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
def samurai(request):
    amount = 1
    response= None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("samurai")
            response = merchant.purchase(amount,credit_card)
    else:
        form = CreditCardForm(initial={'number':'4111111111111111'})
    return render(request, 'app/index.html',{'form': form,
                                             'amount':amount,
                                             'response':response,
                                             'title':'Samurai'})

   


def offsite_paypal(request):
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
    pay_pal_obj.add_fields(paypal_params)
    template_vars = {"obj": pay_pal_obj, 'title': 'PayPal Offsite'}
    return render(request, 'app/offsite_paypal.html', template_vars)

def offsite_google_checkout(request):
    return_url = request.build_absolute_uri(reverse('app_offsite_google_checkout_done'))
    fields = {'items': [{'amount': 1,
                         'name': 'name of the item',
                         'description': 'Item description',
                         'id': '999AXZ',
                         'currency': 'USD',
                         'quantity': 1,
                        }],
              'return_url': return_url,}
    google_checkout_obj.add_fields(fields)
    template_vars = {'title': 'Google Checkout', "gc_obj": google_checkout_obj}
    
    return render(request, 'app/google_checkout.html', template_vars)

def offsite_world_pay(request):
    fields = {"instId": settings.WORLDPAY_INSTALLATION_ID_TEST,
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
              "site": "%s://%s" %("https" if request.is_secure() else "http",
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

def offsite_samurai(request):
    template_vars = {'title': 'Samurai Integration', 
                     "samurai_obj": samurai_obj}
    return render(request, "app/samurai.html", template_vars)

