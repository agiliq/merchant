======================
Writing a new gateway
======================

Writing a new gateway for Merchant_ is very easy. Here are the steps
to follow to write a new gateway:

* Create a new gateway file under the `billing.gateways` module which
  should follow this naming convention::

    <gateway_name>_gateway.py

  So for example, PayPal would have `pay_pal_gateway.py`. Similarly, 
  Authorize.Net, would have `authorize_net_gateway.py`.
* Create a class in this file with the following name::

    class GatewayNameGateway(Gateway):
    ...

  So for PayPal, it would be `PayPalGateway` and for Authorize.Net,
  it would be `AuthorizeNetGateway`.
* Implement all or any of following methods in the class::

    def purchase(self, money, credit_card, options = None):
    ...

    def authorize(self, money, credit_card, options = None):
    ...

    def capture(self, money, authorization, options = None):
    ...

    def void(self, identification, options = None):
    ...

    def credit(self, money, identification, options = None):
    ...

    def recurring(self, money, creditcard, options = None):
    ...

    def store(self, creditcard, options = None):
    ...

    def unstore(self, identification, options = None):
    ...    

.. _Merchant: http://github.com/agiliq/merchant 
