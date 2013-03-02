--------------------------------
PayPal Website Payments Standard
--------------------------------

`PayPal Website Payments Standard`_ (PWS) is an offsite payment processor. This
method of payment is implemented in merchant as a wrapper on top of 
`django-paypal`_. You need to install the package to be able to use this
payment processor.

For a list of the fields and settings attribute expected, please refer to the 
PWS and django-paypal documentation.

After a transaction, PayPal pings the notification URL and all the 
data sent is stored in the `PayPalIPN` model instance that can be 
viewed from the django admin.

Test or Live Mode
-----------------
By default the form renders in test mode with POST against ``sandbox.paypal.com``.
Add following to you `settings.py` to put the form into live mode::

	### Django Merchant
	MERCHANT_TEST_MODE = False
	PAYPAL_TEST = MERCHANT_TEST_MODE

Don't forget to add the settings attributes from ``django-paypal``::

    INSTALLED_APPS = (
        ...,
	'paypal.standard.pdt',
	...)

     MERCHANT_SETTINGS = {
         ...,
	 'pay_pal': {
             "WPP_USER" : '...',
             "WPP_PASSWORD" : '...',
             "WPP_SIGNATURE" : '...',
             "RECEIVER_EMAIL" : '...',
	     # Below attribute is optional
	     "ENCRYPTED": True
	 }
	 ...}

     PAYPAL_RECEIVER_EMAIL = MERCHANT_SETTINGS['pay_pal']['RECEIVER_EMAIL']


Example
-------

In urls.py::

  from billing import get_integration
  pay_pal = get_integration("pay_pal")
  urlpatterns += patterns('',
    (r'^paypal-ipn-handler/', include(pay_pal.urls)),
  )

In views.py::

  >>> from billing import get_integration
  >>> pay_pal = get_integration("pay_pal")
  >>> pay_pal.add_fields({
  ...   "business": "paypalemail@somedomain.com",
  ...   "item_name": "Test Item",
  ...   "invoice": "UID",
  ...   "notify_url": "http://example.com/paypal-ipn-handler/",
  ...   "return_url": "http://example.com/paypal/",
  ...   "cancel_return": "http://example.com/paypal/unsuccessful/",
  ...   "amount": 100})
  >>> return render_to_response("some_template.html", 
  ...                           {"obj": pay_pal},
  ...                           context_instance=RequestContext(request))

In some_template.html::

  {% load paypal from paypal_tags %}
  {% paypal obj %}


Template renders to something like below::

  <form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post"> 
    <input type="hidden" name="business" value="paypalemail@somedomain.com" id="id_business" />
    <input type="hidden" name="amount" value="100" id="id_amount" />
    <input type="hidden" name="item_name" value="Test Item" id="id_item_name" />
    <input type="hidden" name="notify_url" value="http://example.com/paypal-ipn-handler/" id="id_notify_url" />
    <input type="hidden" name="cancel_return" value="http://example.com/paypal/unsuccessful" id="id_cancel_return" />
    <input type="hidden" name="return" value="http://example.com/paypal/" id="id_return_url" />
    <input type="hidden" name="invoice" value="UID" id="id_invoice" />  
    <input type="hidden" name="cmd" value="_xclick" id="id_cmd" />
    <input type="hidden" name="charset" value="utf-8" id="id_charset" />
    <input type="hidden" name="currency_code" value="USD" id="id_currency_code" />
    <input type="hidden" name="no_shipping" value="1" id="id_no_shipping" /> 
    <input type="image" src="https://www.sandbox.paypal.com/en_US/i/btn/btn_buynowCC_LG.gif" border="0" name="submit" alt="Buy it Now" /> 
  </form>

.. _`PayPal Website Payments Standard`: https://merchant.paypal.com/cgi-bin/marketingweb?cmd=_render-content&content_ID=merchant/wp_standard
.. _`django-paypal`: https://github.com/dcramer/django-paypal
