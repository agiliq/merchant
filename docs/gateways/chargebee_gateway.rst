-----------
Chargebee
-----------

`Chargebee`_ is a SAAS that makes subscription billing easy to handle. They also
provide the functionality to plug to multiple gateways in the backend.

.. note::

   You will require the `requests`_ package to get Chargebee to work.

Settings attributes required (optional if you are passing them while initializing 
the gateway) for this integration are:

* ``SITE``: The name of the Chargebee app (or site as they refer). The URL is
  generally of the form "https://{site}.chargebee.com/".  
* ``API_KEY``: This key is provided in your settings dashboard.

Settings attributes::

    MERCHANT_TEST_MODE = True # Toggle for live
    MERCHANT_SETTINGS = {
        "chargebee": {
            "SITE": "some-test",
            "API_KEY": "???",
        }
        ...
    }

Example:
---------

  Simple usage::

    >>> chargebee = get_gateway("chargebee")
    >>> credit_card = CreditCard(first_name="Test", last_name="User",
                                 month=10, year=2011, 
                                 number="4111111111111111", 
                                 verification_value="100")

    # Bill the user for 10 USD per month based on a plan called 'monthly'
    # The 'recurring' method on the gateway is a mirror to the 'store' method
    >>> resp = chargebee.store(credit_card, options = {"plan_id": "monthly"})
    >>> resp["response"]["customer"]["subscription"]["id"]
    ...

    # Cancel the existing subscription
    >>> response = chargebee.unstore(resp["response"]["customer"]["subscription"]["id"])
    >>> response["response"]["subscription"]["status"]
    'cancelled'

    # Bill the user for 1000 USD
    # Technically, Chargebee doesn't have a one shot purchase.
    # Create a plan (called 'oneshot' below) that does a recurring
    # subscription with an interval of a decade or more
    >>> resp = chargebee.purchase(1000, credit_card,
        options = {"plan_id": "oneshot", "description": "Quick Purchase"})
    >>> resp["response"]["invoice"]["subscription_id"]
    ...

    # Authorize the card for 100 USD
    # Technically, Chargebee doesn't have a one shot authorize.
    # Create a plan (called 'oneshot' below) that does a recurring
    # subscription with an interval of a decade or more and authorizes
    # the card for a large amount
    >>> resp = chargebee.authorize(100, credit_card,
        options = {"plan_id": "oneshot", "description": "Quick Authorize"})

    # Capture funds (90 USD) from a previously authorized transaction
    >>> response = chargebee.capture(90, resp["response"]["subscription"]["id"])
    >>> response["status"]
    'SUCCESS'

    # Void an authorized transaction
    >>> resp = chargebee.void(resp["response"]["invoice"]["subscription_id"])
    >>> resp["status"]
    'SUCCESS'

.. _`Chargebee`: http://www.chargebee.com/
.. _`requests`: http://docs.python-requests.org/en/latest/index.html
