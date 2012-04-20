----------------------------------------
Samurai Payment Integration
----------------------------------------

`Samurai  Payment Integration`_ is a service offered by 
`FeeFighters`_ to reduce the complexity of PCI compliance.

.. note::

   This integration makes use of the official `samurai`_ python package offered
   by Samurai  Payments. Please install it before you use this integration.

Refer to the :doc:`Samurai Payment <gateways/samurai_gateway>` Gateway for the settings attributes.

Here are the methods and attributes implemented on the ``SamuraiIntegration`` class:

* ``__init__(self, options=None)``: The constructor method 

* ``get_urls(self)``: The method sets the url to which the token is sent
  after the it is obtained from Samurai. This method is generally mapped 
  directly in the ``urls.py``.

  .. code::

     from billing import get_integration

     samurai = get_integration("samurai")

     urlpatterns += patterns('',
        (r'^samurai/', include(samurai_obj.urls)),
     )

* ``transaction(self, request)``: The view method that recieves the
token   

* ``generate_form(self)``: The method that generates and returns the form (present in 
  ``billing.forms.samurai_forms``) 


Example:
--------

    In <some_app>/integrations/samurai_example_integration.py::

       from billing.integrations.samurai_integration import SamuraiIntegration

       class SamuraiExampleIntegration(SamuraiIntegration):
           class transaction(self, request):
               # The token is received in the POST request
               resp = self.samurai_gateway.purchase(100, request.POST["payment_method_token"])
	       if resp["status"] == "SUCCESS":
                   # Redirect if the transaction is successful
                   ...
               else:
                   # Transaction failed
                   ...


    In the views.py::

       samurai_obj = get_integration("samurai_example")
       return render_to_response("some_template.html", 
                               {"samurai_obj": samurai_obj},
                                context_instance=RequestContext(request))

   In the urls.py::

      samurai_obj = get_integration("samurai_example")
      urlpatterns += patterns('',
         (r'^samurai/', include(samurai_obj.urls)),
      )
      
   In the template::

      {% load samurai_payment from samurai_tags %}

      {% samurai_payment samurai_obj %}


.. _`Samurai Payment`: https://samurai.feefighters.com/
.. _`samurai`: http://pypi.python.org/pypi/samurai
.. _`FeeFighters`: http://feefighters.com/
