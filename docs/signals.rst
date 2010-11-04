--------
Signals
--------

The signals emitted by Merchant_ are:

* `transaction_was_successful(sender, type=..., response=...)`: This signal is
  dispatched when a payment is successfully transacted. The `sender` is the
  object which has dispatched the signal. `type` is the kind of transaction.
  Current choices for type are:

  * `purchase`
  * `authorize`
  * `capture`
  * `credit`
  * `void`
  * `store`
  * `unstore`

  `response` is the actual response object that is sent after the success.
  Please consult the individual gateway docs for the response object.
* `transaction_was_unsuccessful(sender, type=..., response=...)`: This signal
  is dispatched when a payment fails. The `sender` is the object which has 
  dispatched the signal. `type` is the kind of transation. Current choices for
  type are:

  * `purchase`
  * `authorize`
  * `capture`
  * `credit`
  * `void`
  * `store`
  * `unstore`

  `response` is the actual response object that is sent after the success.

  .. note:: 

    Some gateways are implemented to raise an error on failure. This exception
    may be passed as the response object. Please consult the docs to confirm.

.. _Merchant: http://github.com/agiliq/merchant
