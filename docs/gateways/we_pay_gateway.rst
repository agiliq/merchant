---------------
WePay Payments
---------------

`WePay.com`_ is a service that lets you accept payments not just from 
credit cards but also from bank accounts.

WePay works slightly differently and is a hybrid between a :doc:`Gateway <gateways>`
and an :doc:`Integration <offsite_processing>` but should still be fairly easy to use.

.. note::

   You will require the official `wepay`_ python package offered by WePay.

Settings attributes required for this integration are:

* ``CLIENT_ID``: This attribute refers to the application id that can be obtained 
  from the account dashboard.
* ``CLIENT_SECRET``: This is the secret for the corresponding ``CLIENT_ID``.
* ``ACCOUNT_ID``: Refers to the WePay user account id. If you are accepting payments 
  for yourself, then this attribute is compulsory. If you are accepting payments for
  other users (say in a marketplace setup), then it is optional in the ``settings.py``
  file but has to be passed in the options dictionary (with the key ``account_id``) 
  in the views.
* ``ACCESS_TOKEN``: The OAuth2 access token acquired from the user after the 
  installation of the WePay application. If you are accepting payments for yourself,
  then this attribute is compulsory. If you are accepting payments for other users
  (say in a marketplace setup), then it is optional in the ``settings.py`` file but
  has to be passed in the options dictionary (with the key ``token``) in the views.


Settings attributes::

    MERCHANT_TEST_MODE = True # Toggle for live
    MERCHANT_SETTINGS = {
        "we_pay": {
            "CLIENT_ID": "???",
            "CLIENT_SECRET": "???",
	    "ACCESS_TOKEN": "???",
	    "ACCOUNT_ID": "???"
        }
        ...
    }


Example:
---------

  Simple usage::

    wp = get_gateway("we_pay")
    credit_card = CreditCard(first_name="Test", last_name="User",
                             month=10, year=2012, 
                             number="4242424242424242", 
                             verification_value="100")

    def we_pay_purchase(request):
        # Bill the user for 10 USD
	# Credit card is not required here because the user
	# is redirected to the wepay site for authorization
    	resp = wp.purchase(10, None, {
	    "description": "Product Description",
	    "type": "GOODS",
	    "redirect_uri": "http://example.com/success/redirect/"
	})
    	if resp["status"] == "SUCCESS":
	    return HttpResponseRedirect(resp["response"]["checkout_uri"])
	...

    # Authorize the card for 1000 USD
    def we_pay_authorize(request):
        # Authorize the card, the amount is not required.
        resp = wp.authorize(None, credit_card, {"customer": {"email": "abc@example.com"}, "billing_address": {"city": ...}})
	resp["checkout_id"]
	...

    # Capture funds from a previously authorized transaction
    def we_pay_capture(request):
        # No ability to partially capture and hence first argument is None
        resp = wp.capture(None, '<authorization_id>')
	...

    # Refund a transaction
    def we_pay_refund(request):
        # Refund completely
        resp = wp.credit(None, '<checkout_id>')
	...
	# Refund partially from a transaction charged $15
	resp = wp.credit(10, '<checkout_id>')
	...
   
    # Store Customer and Credit Card information in the vault
    def we_pay_store(request)
        resp = wp.store(credit_card, {"customer": {"email": "abc@example.com"}, "billing_address": {"city": ...}})
	...

    # A recurring plan for $100/month
    def we_pay_recurring(request):
        options = {"period": "monthly", "start_time": "2012-01-01",
	           "end_time": "2013-01-01", "auto_recur": "true",
		   "redirect_uri": "http://example.com/redirect/success/"}
        resp = wp.recurring(100, None, options = options)
    	if resp["status"] == "SUCCESS":
	    return HttpResponseRedirect(resp["response"]["preapproval_uri"])
	...

.. _`WePay.com`: https://www.wepay.com/
.. _`wepay`: http://pypi.python.org/pypi/wepay/
