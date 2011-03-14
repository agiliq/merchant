---------
WorldPay
---------

WorldPay_, provides a hosted payments page for offsite transactions for 
merchants who cannot guarantee PCI compliance. The documentation for
the service is available here_.

After a transaction, WorldPay pings the notification URL and all the 
data sent is stored in the `RBSResponse` model instance that can be 
viewed from the django admin.

The settings attribute required for this integration are:

* **WORLDPAY_MD5_SECRET_KEY**: The MD5 secret key chosen by the user
  while signing up for the WorldPay Hosted Payments Service.

Example
--------

In urls.py::

  world_pay = get_integration("world_pay")
  urlpatterns += patterns('',
    (r'^world_pay/', include(world_pay.urls)),
    # You'll have to register /world_pay/rbs-notify-handler/ in the
    # WorldPay admin dashboard for the notification URL
  )

In views.py::

  >>> from billing import get_integration
  >>> world_pay = get_integration("world_pay")
  >>> world_pay.add_fields({ 
  ...    "instId": "WP_ID",
  ...    "cartId": "TEST123",
  ...    "amount": 100,
  ...    "currency": "USD",
  ...    "desc": "Test Item",
  ... })
  >>> return render_to_response("some_template.html",
  ...                           {"obj": world_pay},
  ...                           context_instance=RequestContext(request))

In some_template.html::

  {% load billing_tags %}
  {% world_pay obj %}

Template renders to something like below::

    <form method='post' action='https://select-test.wp3.rbsworldpay.com/wcc/purchase'> 
      <input type="hidden" name="futurePayType" id="id_futurePayType" />
      <input type="hidden" name="intervalUnit" id="id_intervalUnit" />
      <input type="hidden" name="intervalMult" id="id_intervalMult" />
      <input type="hidden" name="option" id="id_option" />
      <input type="hidden" name="noOfPayments" id="id_noOfPayments" />
      <input type="hidden" name="normalAmount" id="id_normalAmount" />
      <input type="hidden" name="startDelayUnit" id="id_startDelayUnit" />
      <input type="hidden" name="startDelayMult" id="id_startDelayMult" />
      <input type="hidden" name="instId" value="WP_ID" id="id_instId" />
      <input type="hidden" name="cartId" value="TEST123" id="id_cartId" />
      <input type="hidden" name="amount" value="100" id="id_amount" />
      <input type="hidden" name="currency" value="USD" id="id_currency" />
      <input type="hidden" name="desc" value="Test Item" id="id_desc" />
      <input type="hidden" name="testMode" value="100" id="id_testMode" />
      <input type="hidden" name="signatureFields" value="instId:amount:cartId" id="id_signatureFields" />
      <input type="hidden" name="signature" value="6c165d7abea54bf6c1ce19af60359a59" id="id_signature" /> 
      <input type='submit' value='Pay through WorldPay'/> 
    </form> 
 

.. _WorldPay: http://www.rbsworldpay.com/
.. _here: http://rbsworldpay.com/support/bg/index.php?page=development&sub=integration&c=UK
