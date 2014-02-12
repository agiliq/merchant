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
            "SHARED_SECRET": "???",
            "MERCHANT_ID": "???",
            "SUB_ACCOUNT": "???",
         }
    }

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

    * ``order_id``: string that uniquely identifies the order

  It may include:

    * ``billing_address`` and ``shipping_address``: dictionaries with the items:

      * ``zip_postal_code``: ZIP or post code.
      * ``country``: 2 letter ISO country code.

    * ``currency_code``: which can be ``'GBP'``, ``'USD'`` or ``'EUR'`` (defaults to ``'GBP'``).

    * ``customer_number``: string that uniquely identifies the customer
