========
Changes
========

0.09
----

* Removed Samurai gateway and integration

0.08
-----

* Added bitcoin backend
* Bugfixes to eWay, paypal integration and authorize.net
* Google Checkout shipping, tax rate and private data support
* Changes to Amazon FPS to work with latest boto. Addition of new fields to
  the FPS response model. A backwards incompatible change
* Made merchant django v1.5 compatible
* Fixes in the chargebee gateway broken by changes in the 'requests' api
* Changes to the example to prevent empty forms from raising a Server Error

0.07
-----

* Added Chargebee support
* Added Beanstream gateway

0.06
----

* Added WePay gateway
* Added Authorize.Net Direct Post Method integration

0.05
-----

* Added Paylane gateway support.

0.04
-----

* Backwards incompatible version.
* Changes in the settings attributes. Now there is a single attribute
  for storing the configuration of all gateways and integrations. Check
  the docs for details.
* Changed the usage of the template tags. Refer the docs for details.
* Added a display_name to the integration object. Shouldn't affect users.

0.03
-----

* Added support for Stripe and Samurai gateways and integrations.

0.02
-----

* Added a setup.py and uploaded the package to pypi

0.01
-----

* Initial commit.
