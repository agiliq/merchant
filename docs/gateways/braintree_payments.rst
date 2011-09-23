-----------------------------------
Braintree Payments Server to Server
-----------------------------------

`Braintree Payments Server to Server`_ is a gateway provided by `Braintree Payments`_ 
to services which are willing to take the burden of PCI compliance. This does not involve
any redirects and only Server to Server calls happen in the background.

.. note::

   You will require the official `braintree`_ python package offered by Braintree
   for this gateway to work.

Settings attributes required for this integration are:

* ``BRAINTREE_MERCHANT_ACCOUNT_ID``: The merchant account id provided by Braintree.
  Can be obtained from the account dashboard.
* ``BRAINTREE_PUBLIC_KEY``: The public key provided by Braintree through their account
  dashboard.
* ``BRAINTREE_PRIVATE_KEY``: The private key provided by Braintree through their account
  dashboard.

Example:
---------

  Simple usage::

    >>> braintree = get_gateway("braintree_payments")
    >>> credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2011, 
                                 number="4111111111111111", 
                                 verification_value="100")

    # Bill the user for 1000 USD
    >>> resp = braintree.purchase(1000, credit_card)
    >>> resp["response"].is_success
    True

    # Authorize the card for 1000 USD
    >>> resp = braintree.authorize(1000, credit_card)

    # Capture funds (900 USD) from a previously authorized transaction
    >>> response = braintree.capture(900, resp["response"].transaction.id)
    >>> response["response"].is_success
    True

    # Void an authorized transaction
    >>> braintree.void(resp["response"].transaction.id)

    # Store Customer and Credit Card information in the vault
    >>> options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            }
    >>> resp = braintree.store(credit_card, options = options)

    # Unstore a previously stored credit card from the vault
    >>> response = braintree.unstore(resp["response"].customer.credit_cards[0].token)
    >>> response["response"].is_success
    True

    # A recurring plan charge
    >>> options = {
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                },
            "recurring": {
                "plan_id": "test_plan",
                "trial_duration": 2,
                "trial_duration_unit": "month",
                "number_of_billing_cycles": 12,
                },
            }
    >>> resp = braintree.recurring(10, credit_card, options = options)
    >>> resp["response"].is_success
    True
    >>> resp["response"].subscription.number_of_billing_cycles
    12


.. _`Braintree Payments Server to Server`: http://www.braintreepayments.com/gateway/api
.. _`Braintree Payments`: http://www.braintreepayments.com/
.. _`braintree`: http://pypi.python.org/pypi/braintree/
