
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from app.forms import CreditCardForm

from billing.gateways.authorize_net import AuthorizeNetGateway
from billing.gateways.paypal_card import PaypalCardProcess
from billing.gateways.eway import Eway
from billing.credit_card import CreditCard

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
            merchant = PaypalCardProcess()
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
            merchant = Eway()
            response = merchant.purchase(amount, credit_card, options={'request': request})
    else:
        form = CreditCardForm(initial={'number':'4444333322221111', 
                                       'verification_value': '000',
                                       'month': 7,
                                       'year': 2012})
    return render(request, 'app/index.html', {'form': form, 
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Eway'})

