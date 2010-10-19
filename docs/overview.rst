Merchant: Pluggable and Unified API for Payment Processors
-----------------------------------------------------------

Merchant_, is a django_ app that offers a uniform api and pluggable interface to
interact with a variety of payment processors. It is heavily inspired from Ruby's 
ActiveMerchant_.

Overview
---------

Simple how to::

   # settings.py
   # Authorize.Net settings
   AUTHORIZE_LOGIN_ID = "..."
   AUTHORIZE_TRANSACTION_KEY = "..."

   # PayPal settings
   PAYPAL_TEST = True
   PAYPAL_WPP_USER = "..."
   PAYPAL_WPP_PASSWORD = "..."
   PAYPAL_WPP_SIGNATURE = "..."

   # views.py or wherever you want to use it
   >>> g1 = get_gateway("authorize_net")
   >>>
   >>> cc = CreditCard(first_name= "Test",
   ...                last_name = "User,
   ...                month=10, year=2011,
   ...                number="4222222222222",
   ...                verification_value="100")
   >>>
   >>> response1 = g1.purchase(100, cc, options = {...})
   >>> response1
   {"status": "SUCCESS", "response": <AuthorizeNetAIMResponse object>}
   >>>
   >>> g2 = get_gateway("pay_pal")
   >>>
   >>> response2 = g2.purchase(100, cc, options = {...})
   >>> response2
   {"status": "SUCCESS", "response": <PayPalNVP object>}

.. _Merchant: http://github.com/agiliq/merchant
.. _ActiveMerchant: http://activemerchant.org/
.. _django: http://www.djangoproject.com/
