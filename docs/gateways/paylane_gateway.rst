----------------
Paylane Gateway
----------------

`Paylane`_ is a payment processor focussed mainly in Europe.

.. note::

   You will require `suds`_ python package to work with the 
   the SOAP interface.

Settings attributes required for this gateway are:

* ``USERNAME``: The username provided by Paylane while signing
  up for an account.
* ``PASSWORD``: The password you set from the merchant admin
  panel. Not to be confused with the merchant login password.
* ``WSDL`` (optional): The location of the WSDL file. Defaults
  to https://direct.paylane.com/wsdl/production/Direct.wsdl.
* ``SUDS_CACHE_DIR`` (optional): The location of the suds 
  cache files. Defaults to ``/tmp/suds``.

Settings attributes::

    MERCHANT_TEST_MODE = True # Toggle for live
    MERCHANT_SETTINGS = {
        "paylane": {
            "USERNAME": "???",
            "PASSWORD": "???",
        }
        ...
    }


Example:
---------

  Simple usage::

    >>> paylane = get_gateway("paylane")
    >>> credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2012, 
                                 number="4242424242424242", 
                                 verification_value="100")

    # Bill the user for 1000 USD
    >>> resp = paylane.purchase(1000, credit_card)
    >>> resp["status"]
    SUCCESS

    # Authorize the card for 1000 USD
    >>> resp = paylane.authorize(1000, credit_card)

    # Capture funds (900 USD) from a previously authorized transaction
    >>> response = paylane.capture(900, resp["response"].id)
    >>> response["status"]
    SUCCESS
   
    # A recurring plan charge
    >>> options = {"plan_id": "gold"}
    >>> resp = paylane.recurring(credit_card, options = options)
    >>> resp["status"]
    SUCCESS



.. _`Paylane`: https://paylane.com/
.. _`suds`: https://fedorahosted.org/suds
