
from django.shortcuts import render_to_response
from django.template import RequestContext

from app.forms import CreditCardForm

from merchant.gateways.authorize_net import AuthorizeNetGateway
from merchant.credit_card import CreditCard

def render(request, template, template_vars={}):
    return render_to_response(template, template_vars, RequestContext(request))

def index(request):
    amount = 1
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = AuthorizeNetGateway(login='92KgL2uD', password='4nT73z4473vLJfXF')
            response = merchant.purchase(amount, credit_card)
    else:
        form = CreditCardForm(initial={'number':'4222222222222'})
        response = None
    return render(request, 'app/index.html', {'form': form, 
                                              'amount': amount,
                                              'response': response})
