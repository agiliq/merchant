----------------------------------------
Braintree Payments Transparent Redirect
----------------------------------------

`Braintree Payments Transparent Redirect`_ is a service offered by 
`Braintree Payments`_ to reduce the complexity of PCI compliance.

.. note::

   This integration makes use of the official `braintree`_ python package offered
   by Braintree Payments. Please install it before you use this integration.

Refer to the :doc:`Braintree Payments Server to Server <gateways/braintree_payments>` Gateway for the settings attributes.

Here are the methods and attributes implemented on the ``BraintreePaymentsIntegration`` class:

* ``__init__(self, options=None)``: The constructor method that configures the 
  Braintree environment setting it either to production or sandbox mode based on
  the value of ``settings.MERCHANT_TEST_MODE``.
* ``service_url(self)``: A property that provides the URL to which the Transparent 
  Redirect form is submitted.
* ``get_urls(self)``: The method sets the url to which Braintree redirects
  after the form submission is successful. This method is generally mapped 
  directly in the ``urls.py``.

  .. code::

     from billing import get_integration

     braintree = get_integration("braintree_payments")

     urlpatterns += patterns('',
        (r'^braintree/', include(braintree.urls)),
     )

* ``braintree_notify_handler(self, request)``: The view method that handles the
  confirmation of the transaction after successful redirection from Braintree.
* ``braintree_success_handler(self, request, response)``: If the transaction is
  successful, the ``braintree_notify_handler`` calls the ``braintree_success_handler``
  which renders the ``billing/braintree_success.html`` with the ``response``
  object. The ``response`` object is a standard braintree result described here_.
* ``braintree_failure_handler(self, request, response)``: If the transaction
  fails, the ``braintree_notify_handler`` calls the ``braintree_failure_handler``
  which renders the ``billing/braintree_error.html`` with the ``response`` which
  is a standar braintree error object.
* ``generate_tr_data(self)``: The method that calculates the `tr_data`_ to 
  prevent a form from being tampered post-submission.
* ``generate_form(self)``: The method that generates and returns the form (present in 
  ``billing.forms.braintree_payments_form``) and populates the initial data
  with the ``self.fields`` (added through either the ``add_fields`` or ``add_field``
  methods) and ``tr_data``.


Example:
--------

    In the views.py::

       braintree_obj = get_integration("braintree_payments")
       # Standard braintree fields
       fields = {"transaction": {
                   "order_id": "some_unique_id",
                   "type": "sale",
                   "options": {
                       "submit_for_settlement": True
                     },
                   },
                   "site": "%s://%s" %("https" if request.is_secure() else "http",
                                       RequestSite(request).domain)
                }
       braintree_obj.add_fields(fields)
       return render_to_response("some_template.html", 
                                 {"bp": braintree_obj},
                                 context_instance=RequestContext(request))

   In the urls.py::

      braintree_obj = get_integration("braintree_payments")
      urlpatterns += patterns('',
         (r'^braintree/', include(braintree.urls)),
      )
      
   In the template::

      {% load braintree_payments from braintree_payments_tags %}

      {% braintree_payments bp %}


.. _`Braintree Payments Transparent Redirect`: http://www.braintreepayments.com/gateway/api
.. _`Braintree Payments`: http://www.braintreepayments.com/
.. _`braintree`: http://pypi.python.org/pypi/braintree/
.. _here: http://www.braintreepayments.com/docs/python/transactions/result_handling
.. _`tr_data`: http://www.braintreepayments.com/docs/python/transactions/create_tr#tr_data
