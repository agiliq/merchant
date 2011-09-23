--------------------
Installing Merchant
--------------------

* Clone the git repo from the Merchant_ site and run the setup.py. 
* If you use pip, you could do the following::

    pip install -e git+git://github.com/agiliq/merchant.git#egg=django-merchant

* Install the dependencies for the gateways as prescribed in the individual 
  gateway doc.
* Reference the `billing` app in your settings `INSTALLED_APPS`.

.. _Merchant: http://github.com/agiliq/merchant
