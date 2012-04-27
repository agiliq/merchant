----------------
Google Checkout
----------------

`Google Checkout`_ is an online payment processing solution provided by Google.
The API docs for Google Checkout are available here_.

After a transaction, Google Checkout sends a mail to the subscriber, updates 
the `Merchant Center`_ dashboard and pings the merchant at the Notification
URL. The HTTP POST data is stored in the `GCResponse` model instance that
can be viewed from the django admin.

The setting attributes required for this integration are:

* **MERCHANT_ID**: The merchant id assigned by Google after
  signing up for the service.
* **MERCHANT_KEY**: A secret key assigned by Google after 
  signing up for the service.

Settings attributes::

    MERCHANT_TEST_MODE = True # Toggle for live
    MERCHANT_SETTINGS = {
        "google_checkout": {
            "MERCHANT_ID": "???",
            "MERCHANT_KEY": "???"
        }
        ...
    }

Example
-------

In urls.py::

  gc = get_integration("google_checkout")
  urlpatterns += patterns('',
    (r'^gc/', include(gc.urls)),
    # You'll have to register /gc/gc-notify-handler/ in the
    # WorldPay admin dashboard for the notification URL
  )

In views.py::

  >>> from billing import get_integration
  >>> gc = get_integration("google_checkout")
  >>> gc.add_fields({'items': [{
  ...    "amount": 100,
  ...    "name": "Name of the Item",
  ...    "description": "Item's description",
  ...    "currency": "USD",
  ...    "id": "item_id",
  ...    "quantity": 1},
  ...    ....
  ... ],
  ... "return_url": "http://example.com/return/", })
  >>> return render_to_response("some_template.html",
  ...                           {"obj": gc},
  ...                           context_instance=RequestContext(request))

In some_template.html::

  {% load google_checkout from google_checkout_tags %}
  {% google_checkout obj %}

Template renders to something like below::

  <form action="https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/646831507676008" method="post"> 
    <input type="hidden" name="cart" value="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48Y2hlY2tvdXQtc2hvcHBpbmctY2FydCB4bWxucz0iaHR0cDovL2NoZWNrb3V0Lmdvb2dsZS5jb20vc2NoZW1hLzIiPjxzaG9wcGluZy1jYXJ0PjxpdGVtcz48aXRlbT48aXRlbS1uYW1lPm5hbWUgb2YgdGhlIGl0ZW08L2l0ZW0tbmFtZT48aXRlbS1kZXNjcmlwdGlvbj5JdGVtIGRlc2NyaXB0aW9uPC9pdGVtLWRlc2NyaXB0aW9uPjx1bml0LXByaWNlIGN1cnJlbmN5PSJVU0QiPjE8L3VuaXQtcHJpY2U+PHF1YW50aXR5PjE8L3F1YW50aXR5PjxtZXJjaGFudC1pdGVtLWlkPjk5OUFYWjwvbWVyY2hhbnQtaXRlbS1pZD48L2l0ZW0+PC9pdGVtcz48L3Nob3BwaW5nLWNhcnQ+PC9jaGVja291dC1zaG9wcGluZy1jYXJ0Pg==" /> 
    <input type="hidden" name="signature" value="3jkvhENlILC3GTVNrXwmvldds4U=" /> 
    <input type="image" name="Google Checkout" alt="Fast checkout through Google" src="http://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=646831507676008&amp;w=180&amp;h=46&amp;style=white&amp;variant=text&amp;loc=en_US" height="46" width="180" /> 
  </form> 
 

.. _`Google Checkout`: https://checkout.google.com/
.. _here: http://code.google.com/apis/checkout/
.. _`Merchant Center`: http://code.google.com/apis/checkout/developer/Google_Checkout_Glossary.html#merchant_center
