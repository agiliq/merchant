--------------------
Off-site Processing
--------------------

Off-site processing is the payment mechanism where the customer is
redirected to the payment gateways site to complete the transaction
and is redirected back to the merchant website on completion.

Since the credit card number and other sensitive details are entered
on the payment gateway's site, the merchant website need not comply
to `PCI standards`_. This mode of payment is recommended when the 
merchant website is not in a position to use SSL certificates, not 
able to guarantee a secure network etc

Off-site processing is generally implemented in merchant through
`template tags`_.

.. _`PCI standards`: http://en.wikipedia.org/wiki/Payment_Card_Industry_Data_Security_Standard
.. _`template tags`: http://docs.djangoproject.com/en/dev/topics/templates/#tags
