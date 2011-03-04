-------------
eWay Gateway
-------------

The eWay gateway implements the `eWay Hosted Payment API`_.

.. note::

     Since the eWay payment gateway uses SOAP_, the API has been implemented
     using the suds_ SOAP library for python. You'll require it to be able to
     use this gateway.

Usage
------

* Add the following attributes to your `settings.py`::

    MERCHANT_TEST_MODE = True
    EWAY_CUSTOMER_ID = "???"  # Only used for live transactions
    EWAY_USERAME = "???"
    EWAY_PASSWORD = "???"
    EWAY_TEST_CUSTOMER_ID = "???"  # Used for testing
    
* Use the gateway instance::

    >>> g1 = get_gateway("eway")
    >>>
    >>> cc = CreditCard(first_name= "Test",
    ...                last_name = "User",
    ...                month=10, year=2011,
    ...                number="4222222222222",
    ...                verification_value="100")
    >>>
    >>> response1 = g1.purchase(100, cc, options = {...})
    >>> response1
    {"status": "SUCCESS", "response": <instance>}

.. _`eWay Hosted Payment API`: http://www.eway.com.au/Developer/eway-api/hosted-payment-solution.aspx
.. _SOAP: http://en.wikipedia.org/wiki/SOAP
.. _suds: https://fedorahosted.org/suds/
