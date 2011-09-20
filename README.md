# Django-Merchant

Django-Merchant is a Django application that enables you to use
multiple payment processors from a single API.



## Gateways
Following gateways are supported:

### Creditcard Processing

 * Authorize.net
 * Paypal
 * Eway

### Off-Site Processing

 * Paypal
 * RBS WorldPay
 * Google Checkout
 * Amazon FPS



## Links to Processors

 * https://developer.paypal.com
 * http://aws.amazon.com/fps/
 * https://checkout.google.com/seller/integrate.html
 * http://developer.authorize.net/
 * http://www.rbsworldpay.com/support/bg/index.php

### Paypal Required Settings
For Website Payments Pro:

    INSTALLED_APPS = (... 'paypal.standard', 'paypal.pro', ...)
    PAYPAL_TEST = True
    PAYPAL_WPP_USER = "???"
    PAYPAL_WPP_PASSWORD = "???"
    PAYPAL_WPP_SIGNATURE = "???"



## Documentation
Documentation is automatically build and pushed online, available at:

 * http://readthedocs.org/docs/django-merchant/en/latest/
