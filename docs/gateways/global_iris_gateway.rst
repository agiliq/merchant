===========
Global Iris
===========

This gateway is an implementation of `Global Iris
<https://resourcecentre.globaliris.com/>`_, previously known as HSBC Merchant
Services or Global Payments.

Usage
-----

You will need an account with Global Iris - email
globaliris@realexpayments.com. You will also need to let them know your
server(s) IP address(es).

* Add the following attributes to your `settings.py`::

    MERCHANT_SETTINGS = {
        "global_iris": {
            "TEST": {
                "SHARED_SECRET": "???",
                "MERCHANT_ID": "???",
                "ACCOUNT": "???",
            },
            "LIVE": {
                "SHARED_SECRET": "???",
                "MERCHANT_ID": "???",
                "ACCOUNT": "???",
            },
         }
    }

  The details in 'TEST' are used for some of the automated tests, and if
  MERCHANT_TEST_MODE is True.

  In addition, you may have been provided with separate accounts for different
  credit card types. These can be configured using additional dictionaries,
  with a key composed of 'LIVE_' or 'TEST_' followed by the following strings:

  * 'VISA' for Visa
  * 'MC' for MasterCard
  * 'AMEX' for AmericanExpress


* Use the gateway instance::

    >>> g1 = get_gateway("global_iris")
    >>> cc = Visa(first_name="Joe",
                  last_name="Bloggs",
                  number="4012345678901234",
                  month=12,
                  year=2014,
                  verification_value="456")

    >>> response = g1.purchase(Decimal("15.00"), cc, options={'order_id': 123})
    >>> response
    {"status":"SUCCESS", "message": "Authcode: ...", "response":<Response [200]> }

    >>> response
    {"status:"FAILURE", "message": "...", response_code: 205}


  ``options`` must include the following:

    * ``order_id``: string that uniquely identifies the transaction.

  It may include:

    * ``billing_address`` and ``shipping_address``: dictionaries with the items:

      * ``zip``: ZIP or post code.
      * ``country``: 2 letter ISO country code.

    * ``currency``: which can be ``'GBP'``, ``'USD'`` or ``'EUR'`` (defaults to ``'GBP'``).

    * ``customer``: string that uniquely identifies the customer

* You may want to run the tests::

    ./manage.py test billing


  To run all the test suite, you will need a 'TEST' dictionary in your
  MERCHANT_SETTINGS['global_iris'] dictionary, as above, and you will also need
  to add a list of cards to test in a 'TEST_CARDS' entry as below::

    MERCHANT_SETTINGS = {
      "global_iris": {
          "TEST": {
              "SHARED_SECRET": 'x',
              "MERCHANT_ID": 1234,
              "ACCOUNT": "foo",
              },
          "TEST_CARDS": [
                {
                  'TYPE': 'VISA',
                  'NUMBER': '4263791920101037',
                  'RESPONSE_CODE': '00',
                  },
                ...
              ],
          }
      }
