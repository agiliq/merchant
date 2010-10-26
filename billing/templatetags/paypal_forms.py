'''
Template tags for paypal offsite payments
'''
from string import split

from django.conf import settings

from paypal.standard.forms import PayPalPaymentsForm
from billing.helpers import require 

def paypal_buy(context):
    '''render paypal form to buy item'''
    require(context, *split('notify_url return_url cancel_return amount item_name invoice'))
    
    params = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': context['amount'],
        'item_name': context['item_name'],
        'invoice': context['invoice'],
        'notify_url': context['notify_url'],
        'return_url': context['return_url'],
        'cancel_return': context['cancel_return'],
    }
    
    form = PayPalPaymentsForm(initial=params)
    return {'form': form,
            'test_mode': getattr(settings, 'MERCHANT_TEST_MODE', True)}