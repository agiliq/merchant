------------------------
eWAY Payment Integration
------------------------

The eWAY integration functionality interfaces with eWAY's Merchant Hosted
Payments facility. Their service makes it extremely easy to be PCI-DSS
compliant by allowing you to never receive customer credit card information.

.. note::

   This integration requires the suds__ package. Please install it before you
   use this integration.

__ https://fedorahosted.org/suds/

The basic data flow is as follows:

1. Request an *access code* from eWAY.
2. Create an HTML form with the *access code* and user credit card fields.
3. Encourage the user to submit the form to eWAY and they'll be redirected back
   to your site.
4. Use the *access code* to ask eWAY if the transaction was successful.

You must add the following to project's settings::

    MERCHANT_SETTINGS = {
        "eway": {
            "CUSTOMER_ID": "???",
            "USERNAME": "???",
            "PASSWORD": "???",
        }
    }

The integration class is used to request an *access code* and also to check its
success after the redirect:

.. class:: EwayIntegration(access_code=None)

    Creates an integration object for use with eWAY.

    *access_code* is optional, but must be configured prior to using
    :func:`check_transaction`.


.. function:: request_access_code(payment, redirect_url, customer=None, \
                                  billing_country=None, ip_address=None)

    Requests an *access code* from eWAY to use with a transaction.

    :param         payment: Information about the payment
    :type          payment: dict
    :param    redirect_url: URL to redirect the user to after payment
    :type     redirect_url: unicode
    :param        customer: Customer related information
    :type         customer: dict
    :param billing_country: Customer's billing country
    :type  billing_country: unicode alpha-2 country code (as per ISO 3166)
    :param      ip_address: Customer's IP address
    :type       ip_address: unicode
    :returns: (access_code, customer)

    The integration is automatically updated with the returned access code.

    **Supported keys in** ``customer``:

    ===================== ===========================
    Key                   Notes
    --------------------- ---------------------------
    ``token_customer_id``
    ``save_token``
    ``reference``
    ``title``             required for ``save_token``
    ``first_name``        required for ``save_token``
    ``last_name``         required for ``save_token``
    ``company_name``
    ``job_description``
    ``street``
    ``city``
    ``state``
    ``postal_code``
    ``country``           required for ``save_token``
    ``email``
    ``phone``
    ``mobile``
    ``comments``
    ``fax``
    ``url``
    ===================== ===========================

    **Supported keys in** ``payment``:

    ======================= ==============================
    Key                     Notes
    ----------------------- ------------------------------
    ``total_amount``        *required* (**must be cents**)
    ``invoice_number``
    ``invoice_description``
    ``invoice_reference``
    ======================= ==============================

    To add extra security, it's a good idea to specify ``ip_address``. The
    value is given to eWAY to allow them to ensure that the POST request they
    receive comes from the given address. E.g.::

        def payment(request):
            integration = get_integration("eway_au")
            access_code, customer = integration.request_access_code(..., ip_address=request.META["REMOTE_ADDR"])
            # ...

    **Returned value**

    The returned value is a tuple ``(access_code, customer)``. ``access_code``
    is the access code granted by eWAY that must be included in the HTML form,
    and is used to request transaction status after the redirect.

    ``customer`` is a dict containing information about the customer. This is
    particularly useful if you make use of ``save_token`` and
    ``token_customer_id`` to save customer details on eWAY's servers. Keys in
    the dict are:

    - ``token_customer_id``
    - ``save_token``
    - ``reference``
    - ``title``
    - ``first_name``
    - ``last_name``
    - ``company_name``
    - ``job_description``
    - ``street``
    - ``city``
    - ``state``
    - ``postal_code``
    - ``country`` -- e.g. ``au``
    - ``email``
    - ``phone``
    - ``mobile``
    - ``comments``
    - ``fax``
    - ``url``
    - ``card_number`` -- e.g. ``444433XXXXXX1111``
    - ``card_name``
    - ``card_expiry_month``
    - ``card_expiry_year``


.. function:: check_transaction()

    Check with eWAY what happened with a transaction.

    This method requires ``access_code`` has been configured.

    :returns: dict

    ====================== ======================================
    Key                    Example
    ---------------------- --------------------------------------
    ``access_code``
    ``authorisation_code`` ``"198333"``
    ``response_code``      ``"00"``
    ``response_message``   ``"Transaction Approved"`` or ``None``
    ``option_1``           ``"a1b2c3"``
    ``option_2``
    ``option_3``
    ``invoice_number``     ``"19832261"``
    ``invoice_reference``  ``"19832261-AA12/1"``
    ``total_amount``       ``"1000"``
    ``transaction_id``     ``"7654321"``
    ``transaction_status`` ``True``
    ``error_message``
    ``token_customer_id``  ``"1234567890123456"``
    ``beagle_score``       ``10.23``
    ====================== ======================================


Example:
--------


.. code-block:: python

    # views.py
    from billing import get_integration
    from django.shortcuts import get_object_or_404


    def payment(request, cart_pk):
        # Pretend some 'Order' model exists with a 'total_price' in dollars
        order = get_object_or_404(Order, pk=cart_pk)

        integration = get_integration("eway_au")
        access_code, customer = integration.request_access_code(
            customer={"first_name": "Bradley", "last_name": "Ayers"},
            payment={"total_amount": order.total_price * 100},
            return_url=reverse(payment_done))
        request.session["eway_access_code"] = integration.access_code
        return render(request, "payment.html", {"integration": integration})


    def payment_done(request, cart_pk):
        order = get_object_or_404(Order, pk=cart_pk)
        access_code = request.session["access_code"]
        integration = get_integration("eway_au", access_code=access_code)
        # Retrieve transaction status from eWAY
        status = integration.check_transaction()
        if status["response_code"] in ("00", "08", "11"):
            order.is_paid = True
            order.save()
            template = "receipt.html"
        else:
            template = "payment_failed.html"
        return render(request, template, {"status": status})


In order for eWAY to process the transaction, the user must submit the payment
HTML form directly to eWAY. The helper tag ``{% eway %}`` makes this trivial:

.. code-block:: django

    {% load eway from eway_tags %}
    {% eway integration %}

For a more configurable form, use the following pattern:

.. code-block:: django

    <form method="post" action="{{ integration.service_url }}">
        {{ integration.generate_form.as_p }}
        <input type="submit"/>
    </form>
