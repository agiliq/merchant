----------------------
Authorize.Net Gateway
----------------------

This gateway implements the `Authorize.Net Advanced Integration Method (AIM)`_.

Usage
------

* Setup a `test account`_ with Authorize.Net.
* Add the following attributes to your `settings.py`::

    MERCHANT_TEST_MODE = True         # Toggle for live transactions
    MERCHANT_SETTINGS = {
        "authorize_net": {
            "LOGIN_ID" : "???",
            "TRANSACTION_KEY" : "???"
	}
        ...
    }

* Use the gateway instance::

    >>> g1 = get_gateway("authorize_net")
    >>>
    >>> cc = CreditCard(first_name= "Test",
    ...                last_name = "User",
    ...                month=10, year=2011,
    ...                number="4222222222222",
    ...                verification_value="100")
    >>>
    >>> response1 = g1.purchase(1, cc, options = {...})
    >>> response1
    {"status": "SUCCESS", "response": <AuthorizeNetAIMResponse object>}

.. _`Authorize.Net Advanced Integration Method (AIM)`: http://developer.authorize.net/api/aim/
.. _`test account`: http://developer.authorize.net/testaccount/
