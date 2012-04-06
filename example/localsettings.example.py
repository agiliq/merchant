
DEBUG = True

# MERCHANT SETTINGS
MERCHANT_TEST_MODE = True

# AUTHORIZE.NET SETTINGS
AUTHORIZE_LOGIN_ID = ''
AUTHORIZE_TRANSACTION_KEY = ''

# PAYPAL SETTINGS
PAYPAL_TEST = True
PAYPAL_WPP_USER = ''
PAYPAL_WPP_PASSWORD = ''
PAYPAL_WPP_SIGNATURE = ''
PAYPAL_RECEIVER_EMAIL = ''

# EWAY SETTINGS
EWAY_CUSTOMER_ID = ''
EWAY_USERNAME = ''
EWAY_PASSWORD = ''
EWAY_TEST_CUSTOMER_ID = ''

# GOOGLE CHECKOUT SETTINGS
GOOGLE_CHECKOUT_MERCHANT_ID = 'a'
GOOGLE_CHECKOUT_MERCHANT_KEY = 'b'

# WORLDPAY settings
WORLDPAY_HOSTED_URL_TEST = "https://select-test.wp3.rbsworldpay.com/wcc/purchase"
WORLDPAY_HOSTED_URL_LIVE = "https://secure.wp3.rbsworldpay.com/wcc/purchase"

WORLDPAY_INSTALLATION_ID_TEST = ''
WORLDPAY_INSTALLATION_ID_LIVE = ''

WORLDPAY_MD5_SECRET_KEY = ''

# Amazon FPS settings
AWS_ACCESS_KEY = ''
AWS_SECRET_ACCESS_KEY = ''

# Braintree Payment settings
BRAINTREE_MERCHANT_ACCOUNT_ID = ""
BRAINTREE_PUBLIC_KEY = ""
BRAINTREE_PRIVATE_KEY = ""

#Stripe Payment Settings
STRIPE_API_KEY = ''
STRIPE_PUBLISHABLE_KEY = ''

#SAMURAI Settings
SAMURAI_MERCHANT_KEY = ''
SAMURAI_MERCHANT_PASSWORD = ''
SAMURAI_PROCESSOR_TOKEN = ''

#OGONE Settings
SHA_PRE_SECRET = 'test1234'
SHA_POST_SECRET = 'test12345'
HASH_METHOD = 'sha512'
PRODUCTION = False
PSPID = 'mypspid'

OGONE_TEST_URL = 'https://secure.ogone.com/ncol/test/orderstandard.asp'
OGONE_PROD_URL = 'https://secure.ogone.com/ncol/prod/orderstandard.asp'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tmp/merchant.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
