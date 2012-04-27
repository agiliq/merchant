--------------------
Off-site Processing
--------------------

Off-site processing is the payment mechanism where the customer is
redirected to the payment gateways site to complete the transaction
and is redirected back to the merchant website on completion.

Since the credit card number and other sensitive details are entered
on the payment gateway's site, the merchant website may not comply
to `PCI standards`_. This mode of payment is recommended when the 
merchant website is not in a position to use SSL certificates, not 
able to guarantee a secure network etc

Off-site processing is generally implemented in merchant through
`Integrations` (name derived from `Active Merchant`_).

Integration
------------

An Integration much like a :doc:`Gateway <gateways>` is a Python class.
But unlike a Gateway which is used in a view, an Integration renders 
a form (usually with hidden fields) through a template tag. An
integration may also support asynchronous and real-time transaction
status handling through callbacks or notifiers like the `PayPal IPN`_

Here is a reference of the attributes and methods of the Integration 
class:

Attributes
++++++++++

* **fields**: Dictionary of form fields that have to be rendered in the
  template.
* **test_mode**: Signifies if the integration is in a test mode or 
  production. The default value for this is taken from the `MERCHANT_TEST_MODE`
  setting attribute.
* **display_name**: A human readable name that is generally used to tag the 
  errors when the integration is not correctly configured.

Methods
+++++++

* **__init__(options={})**: The constructor for the Integration.
  The options dictionary if present overrides the default items of the
  fields attribute.
* **add_field(key, value)**: A method to modify the fields attribute.
* **add_fields(fields)**: A method to update the fields attribute with
  the fields dictionary specified.
* **service_url**: The URL on the form where the fields data is posted.
  Overridden by implementations.
* **get_urls**: A method that returns the urlpatterns for the notifier/
  callback. This method is modified by implementations.
* **urls**: A property that returns the above method.

Helper Function
+++++++++++++++

Very much like :doc:`Gateways <gateways>`, Integrations have a method of easily
referencing the corresponding integration class through the `get_integration`
helper function.

* **get_integration(integration_name, *args, \*\*kwargs)**: Returns the 
  Integration class for the corresponding `integration_name`.

Example::

  >>> from billing import get_integration
  >>> get_integration("pay_pal")
  <billing.integrations.pay_pal_integration.PayPalIntegration object at 0xa57e12c>

.. _`PCI standards`: http://en.wikipedia.org/wiki/Payment_Card_Industry_Data_Security_Standard
.. _`Active Merchant`: http://activemerchant.org/
.. _`PayPal IPN`: https://www.paypal.com/ipn
