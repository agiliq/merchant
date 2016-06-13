import datetime
from django.conf import settings
from django.core.urlresolvers import reverse

from billing.utils.paylane import (
    PaylanePaymentCustomer,
    PaylanePaymentCustomerAddress
)
from .utils import randomword

HOST = getattr(settings, "HOST", "http://127.0.0.1")

COMMON_INITIAL = {
    'first_name': 'John',
    'last_name': 'Doe',
    'month': '06',
    'year': '2020',
    'card_type': 'visa',
    'verification_value': '000'
}

GATEWAY_INITIAL = {
    'authorize_net': {
        'number': '4222222222222',
        'card_type': 'visa',
        'verification_value': '100'
    },
    'paypal': {
        'number': '4797503429879309',
        'verification_value': '037',
        'month': 1,
        'year': 2019,
        'card_type': 'visa'
    },
    'eway': {
        'number': '4444333322221111',
        'verification_value': '000'
    },
    'braintree_payments': {
        'number': '4111111111111111',
    },
    'stripe': {
        'number': '4242424242424242',
    },
    'paylane': {
        'number': '4111111111111111',
    },
    'beanstream': {
        'number': '4030000010001234',
        'card_type': 'visa',
        'verification_value': '123'
    },
    'chargebee': {
        'number': '4111111111111111',
    }
}

INTEGRATION_INITIAL = {
    'stripe': {
        'amount': 1,
        'credit_card_number': '4222222222222',
        'credit_card_cvc': '100',
        'credit_card_expiration_month': '01',
        'credit_card_expiration_year': '2020'
    },
    'authorize_net_dpm': {
        'x_amount': 1,
        'x_fp_sequence': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        'x_fp_timestamp': datetime.datetime.now().strftime('%s'),
        'x_recurring_bill': 'F',
        'x_card_num': '4007000000027',
        'x_exp_date': '01/20',
        'x_card_code': '100',
        'x_first_name': 'John',
        'x_last_name': 'Doe',
        'x_address': '100, Spooner Street, Springfield',
        'x_city': 'San Francisco',
        'x_state': 'California',
        'x_zip': '90210',
        'x_country': 'United States'
    },

    'paypal': {
        'amount_1': 1,
        'item_name_1': "Item 1",
        'amount_2': 2,
        'item_name_2': "Item 2",
        'invoice': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        'return_url': '{HOST}/invoice'.format(HOST=HOST),
        'cancel_return': '{HOST}/invoice'.format(HOST=HOST),
        'notify_url': '{HOST}/merchant/paypal/ipn'.format(HOST=HOST),
    },

    'google_checkout': {
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
                    "description": "Congratulations! Your subscription is being set up."
                },
        }],
        'return_url': '{HOST}/invoice'.format(HOST=HOST)
    },

    'amazon_fps': {
        "transactionAmount": "100",
        "pipelineName": "SingleUse",
        "paymentReason": "Merchant Test",
        "paymentPage": "{HOST}/integration/amazon_fps/".format(HOST=HOST),
        "returnURL": '{HOST}/invoice'.format(HOST=HOST)
    },

    'eway_au': {
        'EWAY_CARDNAME': 'John Doe',
        'EWAY_CARDNUMBER': '4444333322221111',
        'EWAY_CARDMONTH': '01',
        'EWAY_CARDYEAR': '2020',
        'EWAY_CARDCVN': '100',
    },

    "braintree_payments": {
        "transaction": {
            "order_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "type": "sale",
            "options": {
                "submit_for_settlement": True
            },
        },
        "site": "{HOST}:8000".format(HOST=HOST)
    },

    "ogone_payments": {
        'orderID': randomword(6),
        'currency': u'INR',
        'amount': u'10000',  # Rs. 100.00
        'language': 'en_US',
        'exceptionurl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
        'declineurl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
        'cancelurl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
        'accepturl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
    }
}

for k, v in GATEWAY_INITIAL.items():
    v.update(COMMON_INITIAL)

for k, v in INTEGRATION_INITIAL.items():
    v.update(COMMON_INITIAL)
