-----------------------------------
Stripe Payments
-----------------------------------

`Stripe Payments`_ is a gateway provided by `Stripe`_ 
to services which are willing to take the burden of PCI compliance. This does not involve
any redirects and only Server to Server calls happen in the background.

.. note::

   You will require the official `stripe`_ python package offered by Stripe
   for this gateway to work.

Settings attributes required for this integration are:

* ``API_KEY``: The merchant api key is provided by Stripe.
  Can be obtained from the account dashboard.

Settings attributes::

    MERCHANT_TEST_MODE = True # Toggle for live
    MERCHANT_SETTINGS = {
        "stripe": {
            "API_KEY": "???",
            "PUBLISHABLE_KEY": "???", # Used for stripe integration
        }
        ...
    }


Example:
---------

  Simple usage::

    >>> from billing import get_gateway, CreditCard
    >>> stripe = get_gateway("stripe")
    >>> credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2012, 
                                 number="4242424242424242", 
                                 verification_value="100")

    # Bill the user for 1000 USD
    >>> resp = stripe.purchase(1000, credit_card)
    >>> resp["status"]
    SUCCESS

    # Authorize the card for 1000 USD
    >>> resp = stripe.authorize(1000, credit_card)

    # Capture funds (900 USD) from a previously authorized transaction
    >>> response = stripe.capture(900, resp["response"].id)
    >>> response["status"]
    SUCCESS

   
    # Store Customer and Credit Card information in the vault
    >>> resp = stripe.store(credit_card)

    # Unstore a previously stored credit card from the vault
    >>> response = stripe.unstore(resp["response"].id)
    >>> response["status"]
    SUCCESS

    # A recurring plan charge
    >>> options = {"plan_id": "gold"}
    >>> resp = stripe.recurring(credit_card, options = options)
    >>> resp["status"]
    SUCCESS



.. _`Stripe Payments Docs`: https://stripe.com/docs
.. _`Stripe Payments`: https://stripe.com/
.. _`stripe`: http://pypi.python.org/pypi/stripe/
