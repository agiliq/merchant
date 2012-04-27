---------------
PayPal Gateway
---------------

.. note::

   This gateway is a wrapper to the django-paypal_ package. Please download
   it to be able to use the gateway.

The PayPal gateway is an implementation of the `PayPal Website Payments Pro`_ 
product.

Usage
-----

* Setup a PayPal Website Payments Pro account and obtain the API details.
* Add `paypal.standard` and `paypal.pro` (apps from django-paypal_) to the 
  `INSTALLED_APPS` in your `settings.py`.
* Also add the following attributes to your `settings.py`::

    MERCHANT_TEST_MODE = True    # Toggle for live transactions
    MERCHANT_SETTINGS = {
        "pay_pal": {
            "WPP_USER" : "???",
            "WPP_PASSWORD" : "???",
            "WPP_SIGNATURE" : "???"
        }
    }

    # Since merchant relies on django-paypal
    # you have to additionally provide the
    # below attributes
    PAYPAL_TEST = MERCHANT_TEST_MODE
    PAYPAL_WPP_USER = MERCHANT_SETTINGS["pay_pal"]["WPP_USER"]
    PAYPAL_WPP_PASSWORD = MERCHANT_SETTINGS["pay_pal"]["WPP_PASSWORD"]
    PAYPAL_WPP_SIGNATURE = MERCHANT_SETTINGS["pay_pal"]["WPP_SIGNATURE"]

* Run `python manage.py syncdb` to get the response tables.
* Use the gateway instance::

    >>> g1 = get_gateway("pay_pal")
    >>>
    >>> cc = CreditCard(first_name= "Test",
    ...                last_name = "User",
    ...                month=10, year=2011,
    ...                number="4222222222222",
    ...                verification_value="100")
    >>>
    >>> response1 = g1.purchase(100, cc, options = {...})
    >>> response1
    {"status": "SUCCESS", "response": <PayPalNVP object>}

.. _django-paypal: http://github.com/dcramer/django-paypal/
.. _`PayPal Website Payments Pro`: https://merchant.paypal.com/cgi-bin/marketingweb?cmd=_render-content&content_ID=merchant/wp_pro
