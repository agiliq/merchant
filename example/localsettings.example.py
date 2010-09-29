
DEBUG = True

# AUTHORIZE.NET SETTINGS
AUTHORIZE_LOGIN_ID = ''
AUTHORIZE_TRANSACTION_KEY = ''

# PAYPAL SETTINGS
PAYPAL_TEST = True
PAYPAL_WPP_USER = ''
PAYPAL_WPP_PASSWORD = ''
PAYPAL_WPP_SIGNATURE = ''
PAYPAL_RECEIVER_EMAIL = ''

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
