--------------------
Installing Merchant
--------------------

You can use any of the following methods to install merchant.

* The recommended way is to install from PyPi_::

    pip install django-merchant

* If you are feeling adventurous, you might want to run the code off
  the git repository::

    pip install -e git+git://github.com/agiliq/merchant.git#egg=django-merchant


Post-installation
------------------

* Install the dependencies for the gateways as prescribed in the individual
  gateway doc.
* Reference the `billing` app in your settings `INSTALLED_APPS`.
* Run `python manage.py syncdb` to create the new required database tables

Configuration
--------------

To configure a gateway/integration add the corresponding key to
`MERCHANT_SETTINGS`. Take a look at `local.py-dist` for reference.

Running the Test Suite
-----------------------

By default, the test suite is configured to run tests for all the gateways and
integrations which are configured::

    python manage.py test billing

Tests for gateways and integrations which are not configured will be skipped.

If you are planning to integrate your app with a specific gateway/integration
then you might wish to run only that apps test suite. For example, to run the
`Google Checkout Integration` test case::

    python manage.py test billing.GoogleCheckoutTestCase

.. _Merchant: http://github.com/agiliq/merchant
.. _PyPi: http://pypi.python.org/pypi/django-merchant
