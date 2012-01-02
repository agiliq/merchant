----------------------------------------
Stripe Payment Integration
----------------------------------------

`Stripe Payment Integration`_ is a service offered by 
`Stripe Payment`_ to reduce the complexity of PCI compliance.

.. note::

   This integration makes use of the official `stripe`_ python package offered
   by Stripe Payments. Please install it before you use this integration.

Settings attributes required for this integration are:



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

* ``get_token(self, request)``: The view method that recieves the
token   

* ``generate_form(self)``: The method that generates and returns the form (present in 
  ``billing.forms.stripe_form``) 


Example:
--------

    In the views.py::

       stripe_obj = get_integration("stripe")
       return render_to_response("some_template.html", 
                               {"stripe_obj": stripe_obj},
                                context_instance=RequestContext(request))

   In the urls.py::

      stripe_obj = get_integration("stripe")
      urlpatterns += patterns('',
         (r'^stripe/', include(stripe_obj.urls)),
      )
      
   In the template::

      {% load billing_tags %}

      {% stripe_payment stripe_obj %}


.. _`Stripe Payment`: https://stripe.com
.. _`stripe`: http://pypi.python.org/pypi/stripe/
.. _`FeeFighters`: http://feefighters.com/
