=========
Gateways
=========

Gateways are the payment processors implemented in Merchant_. This is 
implemented as a class so that it is easy to extend and create as many
gateways as possible.

The base gateway class is `billing.gateway.Gateway` which has the following
methods and attributes.

Attribute Reference
--------------------

* **test_mode**: This boolean attribute signifies if the gateway is in the test
  mode. By default, it looks up this value from the `MERCHANT_TEST_MODE`
  attribute from the settings file. If the `MERCHANT_TEST_MODE` attribute is not
  found in the settings file, the default value is `True` indicating that the 
  gateway is in the test mode. So do not forget to either set the attribute to
  `True` in the subclass or through the settings file.
* **default_currency**: This is the currency in which the transactions are settled
  ie the currency in which the payment gateway sends the invoice, transaction reports
  etc. This does not prevent the developer from charging a customer in other currencies
  but the exchange rate conversion has to be manually handled by the developer. This
  is a string, for example `"USD"` for US Dollar.
* **supported_countries**: This is a `list` of supported countries that are handled
  by the payment gateway. This should contain a list of the country codes as prescribed 
  by the `ISO 3166-alpha 2 standard`_. The `billing.utils.countries` contains a mapping
  of the country names and ISO codes.
* **supported_cardtypes**: This is a `list` of supported card types handled by the
  payment gateway. This should contain a list of instances of the 
  :doc:`CreditCard <credit_card>` class.
* **homepage_url**: A string pointing to the URL of the payment gateway. This is just
  a helper attribute that is currently not used.
* **display_name**: A string that contains the name of the payment gateway. Another
  helper attribute that is currently not used.
* **application_id**: An application name or unique identifier for the gateway. Yet
  another helper attribute not currently used.

Method Reference
-----------------

* **validate_card(credit_card)**: This method validates the supplied card by
  checking if it is supported by the gateway (through the `supported_cardtypes`
  attribute) and calls the `is_valid` method of the card and returns a boolean.
  if the card is not supported by the gateway, a `CardNotSupported` exception
  is raised.
* **service_url**: A property that returns the url to which the credit card
  and other transaction related details are submitted.
* **purchase(money, credit_card, options = None)**: A method that charges the
  given card (one-time) for the given amount `money` using the `options`
  provided. Subclasses have to implement this method.
* **authorize(money, credit_card, options = None)**: A method that authorizes
  (for a future transaction) the credit card for the amount `money` using 
  the `options` provided. Subclasses have to implement this method.
* **capture(money, authorization, options = None)**: A method that captures
  funds from a previously authorized transaction using the `options` 
  provided. Subclasses have to implement this method.
* **void(identification, options = None)**: A method that nulls/voids/blanks
  an authorized transaction identified by `identification` to prevent a 
  subsequent capture. Subclasses have to implement this method.
* **credit(money, identification, options = None)**: A method that refunds a
  settled transaction with the transacation id `identification` and given
  `options`. Subclasses must implement this method.
* **recurring(money, creditcard, options = None)**: A method that sets up a
  recurring transaction (or a subscription). Subclasses must implement
  this method.
* **store(creditcard, options = None)**: A method that stores the credit
  card and user profile information on the payment gateway's servers
  for future reference. Subclasses must implement this method.
* **unstore(identification, options = None)**: A method that reverses the
  `store` method's results. Subclasses must implement this method.

The `options` dictionary passed to the above methods consists of the following
keys:

* **order_id**: A unique order identification code (usually set by the gateway).
* **ip**: The IP address of the customer making the purchase. This is required
  by certain gateways like PayPal.
* **customer**: The name, customer number, or other information that identifies 
  the customer. Optional.
* **invoice**: The invoice code/number (set by the merchant).
* **merchant**: The name or description of the merchant offering the product.
* **description**: A description of the product or transaction.
* **email**: The email address of the customer. Required by a few gateways.
* **currency**: Required when using a currency with a gateway that supports
  multiple currencies. If not specified, the value of the `default_currency` 
  attribute of the gateway instance is used.
* **billing_address**: A dictionary containing the billing address of the 
  customer. Generally required by gateways for address verification (AVS) etc.
* **shipping_address**: A dictionary containing the shipping address of the 
  customer. Required if the merchant requires shipping of products and where
  billing address is not the same as shipping address.

The address dictionary for `billing_address` and `shipping_address` should have
the following keys:

* **name**: The full name of the customer.
* **company**: The company name of the customer. Required by a few gateways.
* **address1**: The primary street address of the customer. Required by many
  gateways.
* **address2**: Additional line for the address. Optional.
* **city**: The city of the customer.
* **state**: The state of the customer.
* **country**: The `ISO 3166-alpha 2 standard`_ code for the country of the 
  customer.
* **zip**: The zip or postal code of the customer.
* **phone**: The phone number of the customer. Optional.

All the above methods return a standard `response` dictionary containing
the following keys:

* **status**: Indicating if the transaction is a "**SUCCESS**" or a 
  "**FAILURE**"
* **response**: The response object for the transaction. Please consult
  the respective gateway's documentation to learn more about it.

Helper functions
-----------------

* **get_gateway(name, *args, **kwargs)**: A helper function that loads the
  gateway class by the `name` and initializes it with the `args` and `kwargs`.

.. _Merchant: http://github.com/agiliq/merchant
.. _`ISO 3166-alpha 2 standard`: http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
