
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from app.forms import CreditCardForm

from billing.gateways.authorize_net import AuthorizeNetGateway
from billing.gateways.paypal_card import PaypalCardProcess
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
            # merchant = AuthorizeNetGateway()
            # response = merchant.purchase(amount, credit_card)
            merchant = PaypalCardProcess()
            response = merchant.purchase(amount, credit_card, options={'request': request})
    else:
        form = CreditCardForm(initial={'number':'4222222222222'})
    return render(request, 'app/index.html', {'form': form, 
                                              'amount': amount,
                                              'response': response})


def authorize(request):
    return HttpResponse('Authorize')


def paypal(request):
    return HttpResponse('Paypal')


def eway(request):
    return HttpResponse('Eway')