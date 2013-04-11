import os
from common import *

from formencode.variabledecode import variable_decode

DEBUG = False


def get_merchant_settings():
    env_dict = dict(filter(lambda x: x[0].startswith('MERCHANT'), os.environ.items()))
    return variable_decode(env_dict, dict_char='__')['MERCHANT']

# MERCHANT SETTINGS
MERCHANT_TEST_MODE = True
MERCHANT_SETTINGS = get_merchant_settings()

# PAYPAL SETTINGS
if MERCHANT_SETTINGS.get("pay_pal"):
    PAYPAL_TEST = MERCHANT_TEST_MODE
    PAYPAL_WPP_USER = MERCHANT_SETTINGS["pay_pal"]["WPP_USER"]
    PAYPAL_WPP_PASSWORD = MERCHANT_SETTINGS["pay_pal"]["WPP_PASSWORD"]
    PAYPAL_WPP_SIGNATURE = MERCHANT_SETTINGS["pay_pal"]["WPP_SIGNATURE"]
    PAYPAL_RECEIVER_EMAIL = MERCHANT_SETTINGS["pay_pal"]["RECEIVER_EMAIL"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'merchant.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
ADMIN_MEDIA_PREFIX = "/static/admin/"
