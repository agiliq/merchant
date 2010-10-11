
import hashlib

from django.conf import settings

from billing.forms import RBSHostedPaymentForm
from required import require 

def rbs_buy(context):
    require(context, *('cart_id amount').split())
    test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)
    secret_key = getattr(settings, "RBS_MD5_SECRET_KEY", None)
    
    form_data = {}
    if test_mode:
        rbs_hosted_url = getattr(settings, "RBS_HOSTED_URL_TEST", "https://select-test.wp3.rbsworldpay.com/wcc/purchase")
        form_data['instId'] = settings.RBS_INSTALLTION_ID_TEST
    else:
        rbs_hosted_url = getattr(settings, "RBS_HOSTED_URL_LIVE", "https://secure.wp3.rbsworldpay.com/wcc/purchase")
        form_data['instId'] = settings.RBS_INSTALLTION_ID_LIVE

    form_data['cartId'] = context['cart_id']
    form_data['amount'] = context["amount"]
    form_data['desc'] = context.get('description', '')
    form_data['currency'] = context.get('currency', 'USD')

    is_recurring = context.get('is_recurring', False)
    if is_recurring:
        billing_interval_unit_map = {
            'day': 1,
            'week': 2,
            'month': 3,
            'year': 4,
        }
        
        form_data['futurePayType'] = 'regular'
        form_data['option'] = 0
        # input number_of_payments is inlucding first month
        # The first payment cannot happen on the day the agreement is set up. 
        # If you want an immediate payment then you can include a standard 
        # payment in the submission to RBS WorldPay.
        form_data['noOfPayments'] = context.get('number_of_payments', 11)
        form_data['intervalUnit'] = billing_interval_unit_map[context.get('billing_interval_unit', 'month').lower()]
        form_data['intervalMult'] = context.get('billing_interval_multiplier', 1)
        if (form_data['intervalUnit'] == 1 and form_data['intervalMult'] < 14) or \
           (form_data['intervalUnit'] == 2 and form_data['intervalMult'] < 2):
            raise TypeError('Minimum billing interval has to be atleast 2 weeks.')
        # same as billing interval unit
        # so that the recurring billing will start after the specified billing innterval
        # as the first interval payment is processed using normal purchase
        form_data['startDelayUnit'] = form_data['intervalUnit']
        # same as billing interval multiplier
        form_data['startDelayMult'] = form_data['intervalMult']
        form_data['normalAmount'] = context.get('recurring_amount', form_data['amount'])
    
    if secret_key:
        md5 = hashlib.md5()
        form_data['signatureFields'] = 'instId:amount:cartId'
        md5.update('%s:%s:%s:%s' % (secret_key, form_data['instId'], form_data['amount'], form_data['cartId']))
        form_data['signature'] = md5.hexdigest()
    
    form_data['testMode'] = 100 if test_mode else 0
    
    form = RBSHostedPaymentForm(initial=form_data)
    
    return {
        'form': form, 
        'rbs_hosted_url': rbs_hosted_url,
    }