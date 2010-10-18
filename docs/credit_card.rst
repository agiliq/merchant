------------
Credit Card
------------

The `CreditCard` class is a helper class with some useful methods mainly for
validation. This class is available in `billing.utils.credit_card`.

Attribute Reference
--------------------

* `regexp`: The compiled regular expression that matches all card numbers for 
  the card issuing authority. For the `CreditCard` class, this is `None`. It 
  is overridden by subclasses.
* `card_type`: Points to a one of `CreditCard`'s subclasses. This attribute is
  set by the `validate_card` method of the selected gateway.
* `card_name`: Card issuing authority name. Generally not required, but some
  gateways expect the user to figure out the credit card type to send  with 
  the requests.

Method Reference
-----------------

* `__init__`: This method expects 6 **compulsory** keyword arguments. They are

  * `first_name`: The first name of the credit card holder.
  * `last_name`: The last name of the credit card holder.
  * `month`: The expiration month of the credit card as an integer.
  * `year`: The expiration year of the credit card as an integer.
  * `number`: The credit card number (generally 16 digits).
  * `verification_value`: The card security code (CVV2).
* `is_luhn_valid`: Checks the validity of the credit card number by using the 
  `Luhn's algorithm` and returns a boolean. This method takes no arguments.
* `is_expired`: Checks if the expiration date of the card is beyond today and
  returns a boolean. This method takes no arguments.
* `valid_essential_attributes`: Verifies if all the 6 arguments provided to the
  `__init__` method are filled and returns a boolean.
* `is_valid`: Checks the validity of the card by calling the `is_luhn_valid`, 
  `is_expired` and `valid_essential_attributes` method and returns a boolean.
  This method takes no arguments.
* `expire_date`: Returns the card expiry date in the "MM-YYYY" format. This is
  also available as a property.
* `name`: Returns the full name of the credit card holder by concatenating the
   `first_name` and `last_name`. This is also available as a property.

.. _`Luhn's algorithm`: http://en.wikipedia.org/wiki/Luhn_algorithm


Subclasses
----------

The various credit cards and debit cards supported by Merchant_ are:

Credit Cards
++++++++++++

* `Visa`

  * card_name = "Visa"
  * regexp = re.compile('^4\d{12}(\d{3})?$')

* `MasterCard`

  * card_name = "MasterCard"
  * regexp = re.compile('^(5[1-5]\d{4}|677189)\d{10}$')

* `Discover`

  * card_name = "Discover"
  * regexp = re.compile('^(6011|65\d{2})\d{12}$')

* `AmericanExpress`

  * card_name = "Amex"
  * regexp = re.compile('^3[47]\d{13}$')

* `DinersClub`

  * card_name = "DinersClub"
  * regexp = re.compile('^3(0[0-5]|[68]\d)\d{11}$')

* `JCB`

  * card_name = "JCB"
  * regexp = re.compile('^35(28|29|[3-8]\d)\d{12}$')

Debit Cards
+++++++++++

* `Switch`

  * card_name = "Switch"
  * regexp = re.compile('^6759\d{12}(\d{2,3})?$')

* `Solo`

  * card_name = "Solo"
  * regexp = re.compile('^6767\d{12}(\d{2,3})?$')

* `Dankort`

  * card_name = "Dankort"
  * regexp = re.compile('^5019\d{12}$')

* `Maestro`

  * card_name = "Maestro"
  * regexp = re.compile('^(5[06-8]|6\d)\d{10,17}$')

* `Forbrugsforeningen`

  * card_name = "Forbrugsforeningen"
  * regexp = re.compile('^600722\d{10}$')

* `Laser`

  * card_name = "Laser"
  * regexp = re.compile('^(6304|6706|6771|6709)\d{8}(\d{4}|\d{6,7})?$')

Helpers
++++++++

* all_credit_cards = [Visa, MasterCard, Discover, AmericanExpress, DinersClub, JCB]

* all_debit_cards  = [Switch, Solo, Dankort, Maestro, Forbrugsforeningen, Laser]

* all_cards = all_credit_cards + all_debit_cards


.. _Merchant: http://github.com/agiliq/merchant
