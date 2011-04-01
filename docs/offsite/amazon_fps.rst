--------------------------------
Amazon Flexible Payment Service
--------------------------------

`Amazon FPS`_, is a service that allows for building very flexible payment systems.
The service can be classified as a part Gateway and part Integration (offsite processor).
This is because the customer is redirected to the Amazon site where he authorizes the
payment and after this the customer is redirected back to the merchant site with a token 
that is used by the merchant to transact with the customer. In plain offsite processors, 
the authorization and transaction take place in one shot almost simultaneously.

Since the service isn't conventional (though very flexible), implementing FPS in merchant
takes a couple of steps more.

The documentation for the service is available at `Amazon FPS Docs`_.

.. note::

   This integration has a dependency on ``boto``, a popular AWS library for python. But
   because of support lacking for FPS, there is a fork available for it here_ with the
   required features.

Settings attributes required for this integration are:

* ``AWS_ACCESS_KEY``: The Amazon AWS access key available from the user's AWS dashboard.
* ``AWS_SECRET_ACCESS_KEY``: The Amazon AWS secret access key also available from the
  user's dashboard. Shouldn't be distributed to anyone.

Here are the methods and attributes implemented on the ``AmazonFpsIntegration`` class:

* ``__init__(options = {})``: The constructor takes a dictionary of options that are
  used to initialize the underlying ``FPSConnection`` that is bundled with ``boto``.
* ``service_url``: A property that returns the API Endpoint depending on whether the
  the integration is in ``test_mode`` or not.
* ``link_url``: A property that returns the link which redirects the customer to the
  Amazon Payments site to authorize the transaction.
* ``purchase(amount, options={})``: The method that charges a customer right away for 
  the amount ``amount`` after receiving a successful token from Amazon. The ``options``
  dictionary is generated from the ``return_url`` on successful redirect from the
  Amazon payments page. This method returns a dictionary with two items, ``status`` 
  representing the status and ``response`` representing the response as described 
  by ``boto.fps.response.FPSResponse``.
* ``authorize(amount, options={})``: Similar to the ``purchase`` method except that 
  it reserves the payment and doesn't not charge until a ``capture`` (settle) is not
  called. The response is the same as that of ``purchase``.
* ``capture(amount, options={})``: Captures funds from an authorized transaction. The
  response is the same as the above two methods.
* ``credit(amount, options={})``: Refunds a part of full amount of the transaction.
* ``void(identification, options={})``: Cancel/Null an authorized transaction.
* ``fps_ipn_handler``: A method that handles the asynchronous HTTP POST request from
  the Amazon IPN and saves into the ``AmazonFPSResponse`` model.
* ``fps_return_url``: This method verifies the source of the return URL from Amazon
  and directs to the transaction.
* ``transaction``: This is the main method that charges/authorizes funds from the 
  customer. This method has to be subclassed to implement the logic for the 
  transaction on return from the Amazon Payments page.

Example
-------

In any app that is present in the ``settings.INSTALLED_APPS``, subclass the 
``AmazonFpsIntegration`` and implement the ``transaction`` method. The file
should be available under ``<app>/integrations/<integration_name>_integration.py``::

    class FpsIntegration(AmazonFpsIntegration):
        # The class name is based on the filename.
	# So if the files exists in <app>/integrations/fps_integration.py
	# then the class name should be FpsIntegration
        def transaction(self, request):
            # Logic to decide if the user should
	    # be charged immediately or funds 
	    # authorized and then redirect the user
	    # Below is an example:
	    resp = self.purchase(10, {...})
	    if resp["status"] == "Success":
	       return HttpResponseRedirect("/success/")
	    return HttpResponseRedirect("/failure/")


In urls.py::

    amazon_fps = get_integration("fps")
    urlpatterns += patterns('',
      (r'^amazon_fps/', include(amazon_fps.urls)),
      # You'll have to register /amazon_fps/fps-notify-handler/ in the
      # Amazon FPS admin dashboard for the notification URL
    )


In views.py::

    def productPage(request):
       amazon_fps = get_integration("fps")
       fields = {"transactionAmount": "100",
                 "pipelineName": "SingleUse",
                 "paymentReason": "Merchant Test",
                 "paymentPage": request.build_absolute_uri(),
                 "returnURLPrefix": "http://merchant.agiliq.com",
                }
        # You might want to save the fields["callerReference"] that
        # is auto-generated in the db or session to uniquely identify
        # this user (or use the user id as the callerReference) because
	# amazon passes this callerReference back in the return URL.
	amazon_fps.add_fields(fields)
	return render_to_response("some_template.html", 
	                          {"fps": amazon_fps},
				  context_instance=RequestContext(request))

.. note::

   The "returnURLPrefix" is not a standard Amazon AWS attribute. It is used
   as a prefix to the return url (which is defined in the get_urls method)
   and by default is /fps-return-url/. The other attributes used in the fields
   are standard and described in the FPS documentation.


In some_template.html::

    {% load billing_tags %}
    {% amazon_fps fps %}

The above template renders the following code::

    <p><a href="https://authorize.payments-sandbox.amazon.com/cobranded-ui/actions/start?callerKey=AKIAI74UIJQ37QS6XLTA&callerReference=5d37ac69-82ac-4bb1-98a4-18c3f9ff15f4&paymentReason=Merchant%20Test&pipelineName=SingleUse&returnURL=http%3A%2F%2Fmerchant.agiliq.com%2Ffps%2Ffps-return-url%2F&signature=wh9PSXAyKfPKizPL%2FRdrYbb24XsoE0efrtMGQBBSs3k%3D&signatureMethod=HmacSHA256&signatureVersion=2&transactionAmount=100"><img src="http://g-ecx.images-amazon.com/images/G/01/cba/b/p3.gif" alt="Amazon Payments" /></a>
  

.. _`Amazon FPS`: http://aws.amazon.com/fps/
.. _`Amazon FPS Docs`: http://aws.amazon.com/documentation/fps/
.. _here: https://github.com/agiliq/boto/
