----------------------------------------
Stripe Payment Integration
----------------------------------------

`Stripe Payment Integration`_ is a service offered by 
`Stripe Payment`_ to reduce the complexity of PCI compliance.

.. note::

   This integration makes use of the official `stripe`_ python package offered
   by Stripe Payments. Please install it before you use this integration.

Refer to the :doc:`Stripe Payments  <gateways/stripe_payment>` Gateway for the settings attributes.

Here are the methods and attributes implemented on the ``StripeIntegration`` class:

* ``__init__(self, options=None)``: The constructor method that configures the 
  stripe setting

* ``get_urls(self)``: The method sets the url to which the token is sent
  after the it is obtained from Stripe. This method is generally mapped 
  directly in the ``urls.py``.

  .. code::

     from billing import get_integration

     stripe = get_integration("stripe")

     urlpatterns += patterns('',
        (r'^stripe/', include(stripe_obj.urls)),
     )

* ``transaction(self, request)``: The method that receives the Stripe Token after
  successfully validating with the Stripe servers. Needs to be subclassed to include
  the token transaction logic.

* ``generate_form(self)``: The method that generates and returns the form (present in 
  ``billing.forms.stripe_form``) 


Example:
--------

    In <some_app>/integrations/stripe_example_integration.py::

       from billing.integrations.stripe_integration import StripeIntegration

       class StripeExampleIntegration(StripeIntegration):
           class transaction(self, request):
               # The token is received in the POST request
               resp = self.stripe_gateway.purchase(100, request.POST["stripeToken"])
	       if resp["status"] == "SUCCESS":
                   # Redirect if the transaction is successful
                   ...
               else:
                   # Transaction failed
                   ...


    In the views.py::

       stripe_obj = get_integration("stripe_example")
       return render_to_response("some_template.html", 
                               {"stripe_obj": stripe_obj},
                                context_instance=RequestContext(request))

   In the urls.py::

      stripe_obj = get_integration("stripe_example")
      urlpatterns += patterns('',
         (r'^stripe/', include(stripe_obj.urls)),
      )
      
   In the template::

      {% load stripe_payment from stripe_tags %}

      {% stripe_payment stripe_obj %}


.. _`Stripe Payment`: https://stripe.com
.. _`stripe`: http://pypi.python.org/pypi/stripe/
