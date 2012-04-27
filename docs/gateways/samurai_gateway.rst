-----------------------------------
Samurai Payments
-----------------------------------

`Samurai Payments`_ is a gateway provided by `FeeFighters`_ 
to services which are willing to take the burden of PCI compliance. This does not involve
any redirects and only Server to Server calls happen in the background.

.. note::

   You will require the official `samurai`_ python package offered by Samurai
   for this gateway to work.

Settings attributes required for this integration are:

* ``MERCHANT_KEY``: The merchant  key  provided by Samurai.
  Can be obtained from the account dashboard.
* ``MERCHANT_PASSWORD``: The merchant password  provided by Samurai through their account
  dashboard.
* ``PROCESSOR_TOKEN``: The processor token  provided by Samurai  through their account
  dashboard.

Settings attributes::

    MERCHANT_TEST_MODE = True # Toggle for live
    MERCHANT_SETTINGS = {
        "samurai": {
            "MERCHANT_KEY": "???",
            "MERCHANT_PASSWORD": "???",
            "PROCESSOR_TOKEN": "???"
        }
        ...
    }

Example:
---------

  Simple usage::

    >>> samurai = get_gateway("samurai")
    >>> credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2012, 
                                 number="4111111111111111", 
                                 verification_value="100")

    # Bill the user for 1000 USD
    >>> resp = samurai.purchase(1000, credit_card)
    >>> resp["response"].is_success()
    True

    # Authorize the card for 1000 USD
    >>> resp = samurai.authorize(1000, credit_card)

    # Capture funds (900 USD) from a previously authorized transaction
    >>> response = samurai.capture(900, resp["response"].reference_id)
    >>> response["response"].is_success()
    True

    # Void an authorized transaction
    >>> samurai.void(resp["response"].reference_id)

    # Store Customer and Credit Card information in the vault
    >>> resp = samurai.store(credit_card)

    # Unstore a previously stored credit card from the vault
    >>> response = samurai.unstore(resp["response"].payment_method_token)
    >>> response["response"].is_redacted
    True

    # Credit the amount back after a purchase
    >>> response = samurai.unstore(1000,credit_card)
    >>> response = samurai.credit(100,response["response"].reference_id)
    >>> response["response"].is_success()
    True



.. _`Samurai Payments`: https://samurai.feefighters.com
.. _`FeeFighters`: http://feefighters.com/
.. _`samurai`: http://pypi.python.org/pypi/samurai/0.6
