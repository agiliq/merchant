
import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from billing.gateways.authorize_net_gateway import AuthorizeNetGateway
from billing.gateways.pay_pal_gateway import PayPalGateway
from billing.gateways.eway_gateway import EwayGateway
from billing.credit_card import CreditCard

from app.forms import CreditCardForm

def render(request, template, template_vars={}):
    return render_to_response(template, template_vars, RequestContext(request))

def index(request, gateway=None):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = AuthorizeNetGateway()
            response = merchant.purchase(amount, credit_card)
    else:
        form = CreditCardForm(initial={'number':'4222222222222'})
    return render(request, 'app/index.html', {'form': form, 
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Authorize'})


def authorize(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = AuthorizeNetGateway()
            response = merchant.purchase(amount, credit_card)
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
            merchant = PayPalGateway()
            response = merchant.purchase(amount, credit_card, options={'request': request})
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
            merchant = EwayGateway()
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
    template_vars = {'title': 'Paypal Offsite'}
    
    # create a unique invoice id
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
    template_vars.update(paypal_params)
    return render(request, 'app/offsite_paypal.html', template_vars)

def offsite_google_checkout(request):
    template_vars = {'title': 'Google Checkout'}
    
    return_url = request.build_absolute_uri(reverse('app_offsite_google_checkout_done'))
    checkout_params = {'amount': 1,
                       'item_name': 'name of the item',
                       'return_url': return_url,}
    template_vars.update(checkout_params)
    return render(request, 'app/google_checkout.html', template_vars)


def offsite_rbs(request):
    template_vars = {'title': 'RBS'}
    checkout_params = {'amount': 1,
                       'cart_id': 'TEST123',
                       'is_recurring': True,
                       # 'billing_interval_unit': 'DAY',
                       # 'billing_interval_multiplier': 7
                       }

    template_vars.update(checkout_params)
    return render(request, 'app/rbs.html', template_vars)
    