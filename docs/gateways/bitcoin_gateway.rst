-------------
Bitcoin Gateway
-------------

The Bitcoin gateway implements the `Bitcoin digital currency`_.

It is implemented using the JSON-RPC API as described in the `Merchant Howto`_.

.. note::

     The Bitcoin gateway depends on the `bitcoin-python` library which
     can be installed from pypi

Usage
------

* Add the following attributes to your `settings.py`::

    "bitcoin": {
        "RPCUSER": "", # you'll find these settings in your $HOME/.bitcoin/bitcoin.conf
        "RPCPASSWORD": "",
        "HOST": "",
        "PORT": "",
        "ACCOUNT": "",
        "MINCONF": 1,
    },

* Use the gateway instance::

    >>> g1 = get_gateway("bitcoin")
    >>> addr = g1.get_new_address()
    >>> # pass along this address to your customer
    >>> # the purchase will only be successful when
    >>> # the amount is transferred to the above address
    >>> response1 = g1.purchase(100, addr, options = {...})
    >>> response1
    {"status": "SUCCESS", "response": <instance>}

.. _`Bitcoin digital currency`: http://bitcoin.org/
.. _`Merchant Howto`: https://en.bitcoin.it/wiki/Merchant_Howto#Using_a_third-party_plugin
