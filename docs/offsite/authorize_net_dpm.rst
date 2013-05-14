----------------------------------------
Authorize.Net Direct Post Method
----------------------------------------

`Authorize.Net Direct Post Method`_ is a service offered by 
`Authorize.Net`_ to reduce the complexity of PCI compliance.

Here are the following settings attributes that are required:

* ``LOGIN_ID``: The Login id provided by Authorize.Net. Can be obtained from the
  dashboard.
* ``TRANSACTION_KEY``: The Transaction key is used to sign the generated form with
  a shared key to validate against form tampering.
* ``MD5_HASH``: This attribute is used to generate a hash that is verified against
  the hash sent by Authorize.Net to confirm the request's source.

Here are the methods and attributes implemented on the ``AuthorizeNetDpmIntegration`` class:

* ``__init__(self)``: The constructor that configures the Authorize.Net Integration 
  environment setting it either to production or sandbox mode based on the value of 
  ``settings.MERCHANT_TEST_MODE``.
* ``form_class(self)``: Returns the form class that is used to generate the form. 
   Defaults to ``billing.forms.authorize_net_forms.AuthorizeNetDPMForm``.
* ``generate_form(self)``: Renders the form and generates some precomputed field
  values.
* ``service_url(self)``: Returns the Authorize.net url to be set on the form.
* ``verify_response(self, request)``: Verifies if the relay response originated
  from Authorize.Net.
* ``get_urls(self)``: The method sets the url to which Authorize.Net sends a relay
  response, redirects on a success or failure.

  .. code::

     from billing import get_integration

     integration = get_integration("authorize_net_dpm")

     urlpatterns += patterns('',
        (r'^authorize_net/', include(integration.urls)),
     )

* ``authorize_net_notify_handler(self, request)``: The view method that handles the
  verification of the response, firing of the signal and sends out the redirect
  snippet to Authorize.Net.
* ``authorize_net_success_handler(self, request)``: The method that renders the
  `billing/authorize_net_success.html`.
* ``authorize_net_failure_handler(self, request)``: The method that renders the 
  `billing/authorize_net_failure.html`.


Example:
--------

    In the views.py::

       int_obj = get_integration("authorize_net_dpm")
       fields = {'x_amount': 1,
                 'x_fp_sequence': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                 'x_fp_timestamp': datetime.datetime.utcnow().strftime('%s'),
                 'x_recurring_bill': 'F',
                }
       int_obj.add_fields(fields)
       return render_to_response("some_template.html", 
                                 {"adp": int_obj},
                                 context_instance=RequestContext(request))

   In the urls.py::

      int_obj = get_integration("authorize_net_dpm")
      urlpatterns += patterns('',
         (r'^authorize_net/', include(int_obj.urls)),
      )
      
   In the template::

      {% load authorize_net_dpm from authorize_net_dpm_tags %}

      {% authorize_net_dpm adp %}


.. _`Authorize.Net Direct Post Method`: http://developer.authorize.net/api/dpm
.. _`Authorize.Net`: http://authorize.net/
