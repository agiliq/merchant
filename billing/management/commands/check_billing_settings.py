
from django.conf import settings

from django.core.management.base import BaseCommand, CommandError

PAYPAL_STANDARD_IPN = ['PAYPAL_RECEIVER_EMAIL']
# PAYPAL_STANDARD_PDT = ['PAYPAL_IDENTITY_TOKEN']
PAYPAL_PRO = ['PAYPAL_TEST', 'PAYPAL_WPP_USER', 'PAYPAL_WPP_PASSWORD', 'PAYPAL_WPP_SIGNATURE']

AUTHORIZE = ['AUTHORIZE_LOGIN_ID', 'AUTHORIZE_TRANSACTION_KEY']
EWAY = ['EWAY_CUSTOMER_ID', 'EWAY_USERNAME', 'EWAY_PASSWORD']
GOOGLE_CHECKOUT = ['GOOGLE_CHECKOUT_MERCHANT_ID', 'GOOGLE_CHECKOUT_MERCHANT_KEY']

PAYMENT_GATEWAYS = {
    'authorize': AUTHORIZE,
    'eway': EWAY,
    'google_checkout': GOOGLE_CHECKOUT,
    'paypal_pro': PAYPAL_PRO,
    'paypal_ipn': PAYPAL_STANDARD_IPN,
}

class Command(BaseCommand):
    help = 'Check for the required settings of billing app'
    args = PAYMENT_GATEWAYS.keys()
    def handle(self, *args, **kwargs):
        check_for_gateway = args or PAYMENT_GATEWAYS.keys()
        
        for gateway in check_for_gateway:
            if gateway not in PAYMENT_GATEWAYS:
                raise CommandError('Invalid payment gateway option %s, valid gateway options are %s' % (gateway, PAYMENT_GATEWAYS.keys()))
            required_settings = PAYMENT_GATEWAYS[gateway]
            for rs in required_settings:
                try:
                    getattr(settings, rs)
                except AttributeError:
                    # raising CommandError because the error message display is neat
                    raise CommandError('Missing parameter %s in settings for %s gateway' % (rs, gateway))
        return '0 errors'