===========
Global Iris
===========

This gateway is an implementation of `Global Iris
<https://resourcecentre.globaliris.com/>`_ RealAuth, previously known as HSBC
Merchant Services or Global Payments.

Normally you will use this in conjunction with the :doc:`Global Iris RealMPI </offsite/global_iris_real_mpi_integration>`.

Usage
-----

You will need an account with Global Iris - email
globaliris@realexpayments.com. You will also need to let them know your
server(s) IP address(es).

* Add the following attributes to your `settings.py`::

    MERCHANT_SETTINGS = {
        "global_iris": {
            "TEST": {
                "SHARED_SECRET": "???",
                "MERCHANT_ID": "???",
                "ACCOUNT": "???",
            },
            "LIVE": {
                "SHARED_SECRET": "???",
                "MERCHANT_ID": "???",
                "ACCOUNT": "???",
            },
         }
    }

  The details in 'TEST' are used for some of the automated tests, and if
  MERCHANT_TEST_MODE is True.

  In addition, you may have been provided with separate accounts for different
  credit card types. These can be configured using additional dictionaries,
  with a key composed of ``'LIVE_'`` or ``'TEST_'`` followed by the following strings:

  * 'VISA' for Visa
  * 'MC' for MasterCard
  * 'AMEX' for AmericanExpress


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

    * ``order_id``: string that uniquely identifies the transaction.

  It may include:

    * ``billing_address`` and ``shipping_address``: dictionaries with the items:

      * ``street_address``: first line of address (includes house number)

      * ``post_code``: post code of address. (``street_address`` and ``post_code`` must both
          be supplied for AVS checks).

      * ``country``: 2 letter ISO country code.

    * ``currency``: which can be ``'GBP'``, ``'USD'`` or ``'EUR'`` (defaults to ``'GBP'``).

    * ``customer``: string that uniquely identifies the customer

    * ``product_id``: product code assigned to the product

    * ``varref``: addition any reference assigned to the customer, which can
      allow checking of previous transactions by this customer, through the use
      of the RealScore service

    * ``customer_ip_address``: IP address of the customer, dotted decimal notation

  If you are using the RealMPI integration, as described above, then the RealAuth
  response may contain a number of other attributes that might be useful:

    * ``avsaddressresponse``: AVS response code for address, as documented in https://resourcecentre.globaliris.com/documents/pdf.html?id=102

    * ``avspostcoderesponse``: AVS response code for post code.

    * ``cvnresult``: (no documentation known for this)

    * ``cardissuer``: dictionary that may contain these keys:

      * ``bank``

      * ``country``

      * ``country_code``

      * ``region``


* You may want to run the tests::

    ./manage.py test billing


  To run all the test suite, you will need a 'TEST' dictionary in your
  MERCHANT_SETTINGS['global_iris'] dictionary, as above, and you will also need
  to add a list of cards to test in a 'TEST_CARDS' entry as below::

    MERCHANT_SETTINGS = {
      "global_iris": {
          "TEST": {
              "SHARED_SECRET": 'x',
              "MERCHANT_ID": 1234,
              "ACCOUNT": "foo",
              },
          "TEST_CARDS": [
                {
                  'TYPE': 'VISA',
                  'NUMBER': '4263791920101037',
                  'RESPONSE_CODE': '00',
                  },
                ...
              ],
          }
      }
