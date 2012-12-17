
DEBUG = True

# MERCHANT SETTINGS
MERCHANT_TEST_MODE = True
MERCHANT_SETTINGS = {
    # AUTHORIZE.NET SETTINGS
    "authorize_net": {
        "LOGIN_ID" : '',
        "TRANSACTION_KEY" : '',
        "MD5_HASH": ''
        },

    # PAYPAL SETTINGS
    "pay_pal": {
        "WPP_USER" : '',
        "WPP_PASSWORD" : '',
        "WPP_SIGNATURE" : '',
        "RECEIVER_EMAIL" : ''
        },

    # EWAY SETTINGS
    "eway": {
        "CUSTOMER_ID" : '',
        "USERNAME" : '',
        "PASSWORD" : '',
        "TEST_CUSTOMER_ID" : ''
        },

    # GOOGLE CHECKOUT SETTINGS
    "google_checkout": {
        "MERCHANT_ID" : '' ,
        "MERCHANT_KEY" : ''
        },

    # WORLDPAY settings
    "world_pay": {
        "HOSTED_URL_TEST" : "https://select-test.wp3.rbsworldpay.com/wcc/purchase",
        "HOSTED_URL_LIVE" : "https://secure.wp3.rbsworldpay.com/wcc/purchase",
        "INSTALLATION_ID_TEST" : '',
        "INSTALLATION_ID_LIVE" : '',
        "MD5_SECRET_KEY" : ''
        },

    # Amazon FPS settings
    "amazon_fps": {
        "AWS_ACCESS_KEY" : '',
        "AWS_SECRET_ACCESS_KEY" : ''
        },

    # Braintree Payment settings
    "braintree_payments": {
        "MERCHANT_ACCOUNT_ID" : "",
        "PUBLIC_KEY" : "",
        "PRIVATE_KEY" : ""
        },

    # Stripe Payment Settings
    "stripe": {
        "API_KEY" : '',
        "PUBLISHABLE_KEY" : ''
        },

    # SAMURAI Settings
    "samurai": {
        "MERCHANT_KEY" : '',
        "MERCHANT_PASSWORD" : '',
        "PROCESSOR_TOKEN" : ''
    },

    # Paylane Settings
    "paylane": {
        "USERNAME": "",
        "PASSWORD": ""
        },

    # WePay Settings
    "we_pay": {
        "CLIENT_ID": "",
        "CLIENT_SECRET": "",
        # Below two are optional if are passed as 
        # extra option items. Useful for marketplace
        "ACCOUNT_ID": "",
        "ACCESS_TOKEN": "",
        },

    "beanstream": {
        "MERCHANT_ID": "",
        "LOGIN_COMPANY": "",
        "LOGIN_USER": "",
        "LOGIN_PASSWORD": "",
        # Below two are optional
        "HASH_ALGORITHM"   : "",
        "HASHCODE"  : ""
    },

    "chargebee": {
        "API_KEY": "",
        "SITE": ""
    },

    "bitcoin": {
        "RPCUSER": "",
        "RPCPASSWORD": "",
        "HOST": "",
        "PORT": "",
        "ACCOUNT": "",
        "MINCONF": 1,
    },
}

# Special case for PayPal because we rely on django-paypal
if MERCHANT_SETTINGS.get("pay_pal"):
    PAYPAL_TEST = MERCHANT_TEST_MODE
    PAYPAL_WPP_USER = MERCHANT_SETTINGS["pay_pal"]["WPP_USER"]
    PAYPAL_WPP_PASSWORD = MERCHANT_SETTINGS["pay_pal"]["WPP_PASSWORD"]
    PAYPAL_WPP_SIGNATURE = MERCHANT_SETTINGS["pay_pal"]["WPP_SIGNATURE"]
    PAYPAL_RECEIVER_EMAIL = MERCHANT_SETTINGS["pay_pal"]["RECEIVER_EMAIL"]

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
