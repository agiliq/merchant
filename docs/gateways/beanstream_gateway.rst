-----------
Beanstream
-----------

`Beanstream`_ is a gateway headquartered in Canada and offering payment processing
across North America.

.. note::

   You will require the `beanstream python package`_ maintained by the community.

Settings attributes required (optional if you are passing them while initializing 
the gateway) for this integration are:

* ``MERCHANT_ID``: The merchant id provided by Beanstream. Can be obtained from the 
  account dashboard.
* ``LOGIN_COMPANY``: The company name as visible from the account settings in the
  dashboard.
* ``LOGIN_USER``: The username used to login to the account dashboard.
* ``LOGIN_PASSWORD``: The password used to login to the account dashboard.
* ``HASH_ALGORITHM``: This is optional but required if you have enabled hashing in 
  account dashboard. The values may be one of `SHA-1` and `MD5`.
* ``HASHCODE``: If the above attribute is enabled, then set this attribute to the
  hash value you've setup in the account dashboard.

Settings attributes::

    MERCHANT_TEST_MODE = True # Toggle for live
    MERCHANT_SETTINGS = {
        "beanstream": {
            "MERCHANT_ID": "???",
            "LOGIN_COMPANY": "???",
            "LOGIN_USER": "???",
            "LOGIN_PASSWORD": "???",
	    # The below two attributes are optional
            "HASH_ALGORITHM": "???",
            "HASHCODE": "???",
        }
        ...
    }

Example:
---------

  Simple usage::

    >>> beanstream = get_gateway("beanstream")
    >>> credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2011, 
                                 number="4111111111111111", 
                                 verification_value="100")

    # Bill the user for 1000 USD
    >>> resp = beanstream.purchase(1000, credit_card)
    >>> resp["response"].resp.approved()
    True

    # Authorize the card for 1000 USD
    >>> resp = beanstream.authorize(1000, credit_card)

    # Capture funds (900 USD) from a previously authorized transaction
    >>> response = beanstream.capture(900, resp["response"].resp["trnId"])
    >>> response["response"].resp.approved()
    True

    # Void an authorized transaction
    >>> beanstream.void(resp["response"].resp["trnId"])

.. _`Beanstream`: http://www.beanstream.com/site/ca/index.html
.. _`beanstream python package`: http://github.com/dragonx/beanstream
