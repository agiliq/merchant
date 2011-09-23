--------------------
Installing Merchant
--------------------

You can use any of the following methods to install merchant.

* pip install django-merchant
* Clone the git repo from the Merchant_ site and run the setup.py. 
* If you use pip, you could do the following::

    pip install -e git+git://github.com/agiliq/merchant.git#egg=django-merchant


Post-installation
------------------

* Install the dependencies for the gateways as prescribed in the individual 
  gateway doc.
* Reference the `billing` app in your settings `INSTALLED_APPS`.

.. _Merchant: http://github.com/agiliq/merchant
