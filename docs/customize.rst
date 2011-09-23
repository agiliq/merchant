---------------------
Customizing Merchant
---------------------

While we make all attempts to cover most of the functionality of the payment
processors but may fall short sometimes. There is absolutely no need to worry
as the gateway and integration objects are extensible.

Merchant_ looks for gateways and integration objects under every ``INSTALLED_APPS``
in ``settings.py``. So it is possible for you to write your custom or modified
objects within your app without having to patch the merchant code.

.. note::

   Most of what is written below will also be applicable for gateways and you will
   have to replace instances of ``integration`` with ``gateway``.

Suppose you want to extend the `Braintree Payments Integration <offsite/braintree_payments>`,
to render to a different template on success instead of the default ``billing/braintree_success.html``.

* In any of the ``INSTALLED_APPS`` in ``settings.py``, create an ``integrations`` module
  (in layman's term an ``integrations`` directory with an ``__init__.py`` file under that
  directory).
* Create a file that follows the convention below::

    <integration_name>_integration.py

  Example::

    Let us name the modified integration as modified_bp, then the filename would be

    modified_bp_integration.py

    and the Integration class name in that file as ModifiedBpIntegration. The name 
    is split on underscores and each element of the split sequence is capitalized.

    class ModifiedBpIntegration(BraintreePaymentsIntegration):
        def braintree_success_handler(self, request, response):
           return render_to_response("my_new_success.html",
	                             {"resp": response}, 
				     context_instance=RequestContext(request))

* Then use the new integration in your code just as you would for a built-in integration::

     >>> bp_obj = get_integration("modified_bp")


.. _Merchant: https://github.com/agiliq/merchant
