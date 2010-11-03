------------------
On-site Processing
------------------

Onsite processing refers to the payment mechanism where the customer stays
on the merchant website and the authentication is done by the merchant 
website with the gateway in the background.

Merchant websites need to comply with `PCI standards`_ to be able to securely
carry out transactions.

On-site processing for payment gateways is implemented by using subclasses
of the :doc:`Gateway class <gateways>`.

.. _`PCI standards`: http://en.wikipedia.org/wiki/Payment_Card_Industry_Data_Security_Standard
