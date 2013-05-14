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

Running the Test Suite
-----------------------

By default, the test suite is configured to run tests for all the gateways and 
integrations::

    python manage.py test billing

This might fail if you have not configured (either the settings attributes or 
the dependencies) the gateways and integrations.

If you are planning to integrate your app with a specific gateway/integration
then you might wish to run only that apps test suite. For example, to run the
`Google Checkout Integration` test case::

    python manage.py test billing.GoogleCheckoutTestCase

.. _Merchant: http://github.com/agiliq/merchant
.. _PyPi: http://pypi.python.org/pypi/django-merchant
