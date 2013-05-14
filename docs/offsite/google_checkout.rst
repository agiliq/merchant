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

  from billing import get_integration
  gc = get_integration("google_checkout")
  urlpatterns += patterns('',
    (r'^gc/', include(gc.urls)),
    # You'll have to add /gc/gc-notify-handler/ to the
    # Google Checkout settings->Integration page for the callback URL
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
  ...    "quantity": 1,
  ...    "private-item-data": "Popular item - order more if needed"},
  ...    ....
  ... ],
  ... "return_url": "http://example.com/return/", })
  >>> return render_to_response("some_template.html",
  ...                           {"obj": gc},
  ...                           context_instance=RequestContext(request))

In some_template.html::

  {% load render_integration from billing_tags %}
  {% render_integration obj %}

Template renders to something like below::

  <form action="https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/646831507676008" method="post"> 
    <input type="hidden" name="cart" value="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48Y2hlY2tvdXQtc2hvcHBpbmctY2FydCB4bWxucz0iaHR0cDovL2NoZWNrb3V0Lmdvb2dsZS5jb20vc2NoZW1hLzIiPjxzaG9wcGluZy1jYXJ0PjxpdGVtcz48aXRlbT48aXRlbS1uYW1lPm5hbWUgb2YgdGhlIGl0ZW08L2l0ZW0tbmFtZT48aXRlbS1kZXNjcmlwdGlvbj5JdGVtIGRlc2NyaXB0aW9uPC9pdGVtLWRlc2NyaXB0aW9uPjx1bml0LXByaWNlIGN1cnJlbmN5PSJVU0QiPjE8L3VuaXQtcHJpY2U+PHF1YW50aXR5PjE8L3F1YW50aXR5PjxtZXJjaGFudC1pdGVtLWlkPjk5OUFYWjwvbWVyY2hhbnQtaXRlbS1pZD48L2l0ZW0+PC9pdGVtcz48L3Nob3BwaW5nLWNhcnQ+PC9jaGVja291dC1zaG9wcGluZy1jYXJ0Pg==" /> 
    <input type="hidden" name="signature" value="3jkvhENlILC3GTVNrXwmvldds4U=" /> 
    <input type="image" name="Google Checkout" alt="Fast checkout through Google" src="http://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=646831507676008&amp;w=180&amp;h=46&amp;style=white&amp;variant=text&amp;loc=en_US" height="46" width="180" /> 
  </form> 


Private Data:
-------------
If you need to add some extra information (order number, etc) you can use the private data field.

The private_data can contain any well-formed XML sequence that should accompany an order. Google Checkout will return this XML in the <merchant-calculation-callback> and the <new-order-notification> for the order.

Example::

    >>> gc.add_fields({'items': ...,
        'private_data': "my order number 76543",
    })

Item
^^^^
You can do the same thing on items as well using the private-item-data field on item. (see view.py example above)

Digital Content:
----------------
The following digital goods identifying are supported: email delivery, key/URL delivery, description-based delivery

Subscriptions:
--------------
The following subscriptions types are supported: google-handled, merchant-handled

Taxes:
------
The following tax methods are supported: default-tax-table and alternate-tax-tables

default-tax-table:
^^^^^^^^^^^^^^^^^^
Here are the examples from the `Google Checkouts Developer Docs <https://developers.google.com/checkout/developer/Google_Checkout_XML_API_Taxes#XML_Examples_for_Tax_Tables>`_ converted to django-merchant

These are only showing the shipping methods section, you still need items and everything else.

Example 1: Charging a single tax rate in one state:
**************************************************
The following example explains how to charge a single tax rate in one state. The example is for a merchant in Connecticut, where there is a 6 percent sales tax. The example contains a single tax rule. In addition, since shipping charges in Connecticut are taxed, the <shipping-taxed> tag is included in this request with a value of true. (If shipping charges are not subject to tax in a state where you charge tax, you can omit the <shipping-taxed> tag from the tax rule for that state or set the tag's value to false.)

XML:

.. code-block:: xml

    <tax-tables>
          <default-tax-table>
            <tax-rules>

              <default-tax-rule>
                <shipping-taxed>true</shipping-taxed>
                <rate>0.0600</rate>
                <tax-area>
                  <us-state-area>
                    <state>CT</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

            </tax-rules>
          </default-tax-table>
        </tax-tables>

Python:

.. code-block:: python 

    >>> gc.add_fields({'items': ... ,
            'tax-tables': {
                'default-tax-table': {
                    'tax-rules': [
                        {
                            'shipping-taxed': True,
                            'rate': 0.0600,
                            'tax-area': {
                                'us-state-area': ['CT'],
                             }
                        }
                    ]
                }
            }
        })


Example 2: Charging tax in two non-overlapping geographic areas
***************************************************************
The following example demonstrates how to create tax tables if you charge tax in more than one geographic area. In this example, the two areas are Connecticut and Maryland. Since the areas do not overlap – a shipping address can only be associated with one state – the tax rules can be specified in any order. As in the previous example, shipping charges in Connecticut are taxed; however, shipping charges in Maryland are not subject to tax.

XML:

.. code-block:: xml

        <tax-tables>
          <default-tax-table>
            <tax-rules>

              <default-tax-rule>
                <shipping-taxed>true</shipping-taxed>
                <rate>0.0600</rate>
                <tax-area>
                  <us-state-area>
                    <state>CT</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

              <default-tax-rule>
                <rate>0.0500</rate>
                <tax-area>
                  <us-state-area>
                    <state>MD</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

            </tax-rules>
          </default-tax-table>
        </tax-tables>


Python:

.. code-block:: python

    >>> gc.add_fields({'items': ... ,
            'tax-tables': {
                    'default-tax-table': {
                        'tax-rules': [
                            {
                                'shipping-taxed': True,
                                'rate': 0.0600,
                                'tax-area': {
                                    'us-state-area': ['CT'],
                                 }
                            },
                            {
                                'rate': 0.0500,
                                'tax-area': {
                                    'us-state-area': ['MD'],
                                 }
                            }
                        ]
                    }
                }
            })


Example 3: Charging tax in two overlapping geographic areas
***********************************************************
The following example also demonstrates how to create tax tables if you charge tax in more than one geographic area. However, in this example, the two areas are in the same state.

- The first area defines a set of zip codes in Manhattan, where there is an 8.375 percent sales tax.
- The second area defines a rule for charging 4 percent sales tax in the state of New York.

Since Google will select the first tax rule that matches the shipping address for the order, the tax rule that defines the narrower geographic area must be listed first. (See the Ordering Tax Rules in XML Requests section for more information.)


XML:

.. code-block:: xml

        <tax-tables>
          <default-tax-table>
            <tax-rules>

              <default-tax-rule>
                <shipping-taxed>false</shipping-taxed>
                <rate>0.08375</rate>
                <tax-area>
                  <us-zip-area>
                    <zip-pattern>100*</zip-pattern>
                  </us-zip-area>
                </tax-area>
              </default-tax-rule>

              <default-tax-rule>
                <shipping-taxed>true</shipping-taxed>
                <rate>0.0400</rate>
                <tax-area>
                  <us-state-area>
                    <state>NY</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

            </tax-rules>
          </default-tax-table>
        </tax-tables>


Python:

.. code-block:: python

    >>> gc.add_fields({'items': ... ,
            'tax-tables': {
                    'default-tax-table': {
                        'tax-rules': [
                            {
                                'shipping-taxed': False,
                                'rate': 0.08375,
                                'tax-area': {
                                    'us-zip-area': ['100*'],
                                 }
                            },
                            {
                                'shipping-taxed': True,
                                'rate': 0.0400,
                                'tax-area': {
                                    'us-state-area': ['NY'],
                                 }
                            }
                        ]
                    }
                }
        })


alternate-tax-tables:
^^^^^^^^^^^^^^^^^^^^^
Alternate tax tables are good for dealing with non-standard taxing issues. For example, having taxable, and tax free items in the same shopping cart.

Example 4: Alternate tax rules
******************************
This example shows how to create an alternate tax table for an item that is tax-exempt. The tax tables in this example indicate that the merchant charges sales tax in Connecticut and Maryland. In Connecticut, sales of bicycle helmets are tax-exempt. (Google does not return any search results indicating that bicycle helmet sales are also tax-exempt in Maryland.)

In this example, the XML contains an alternate tax table for bicycle helmets. That tax table contains one alternate tax rule, which indicates that Connecticut does not charge tax for items associated with that tax table. Please note that value of the <alternate-tax-table> tag's standalone attribute is set to false, which is that element's default value. As a result, if an item specifies the "bicycle helmets" tax table, and there is no alternate tax rule for the shipping address, Google will use the default tax table to calculate tax for the item. Therefore, if the item is shipped to Connecticut, no tax will be charged. However, if the item is shipped to Maryland, the regular tax rate will be assessed.

XML:

.. code-block:: xml

    <shopping-cart>
      <items>
        <item>
          <item-name>Bike Helmet</item-name>
          <item-description>Black helmet that is tax-exempt in CT but not MD.</item-description>
          <unit-price currency="USD">49.99</unit-price>
          <quantity>1</quantity>
          <tax-table-selector>bicycle_helmets</tax-table-selector>
        </item>
      </items>
    </shopping-cart>
    <checkout-flow-support>
      <merchant-checkout-flow-support>
        <tax-tables>
          <default-tax-table>
            <tax-rules>

              <default-tax-rule>
                <shipping-taxed>true</shipping-taxed>
                <rate>0.0600</rate>
                <tax-area>
                  <us-state-area>
                    <state>CT</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

              <default-tax-rule>
                <rate>0.0500</rate>
                <tax-area>
                  <us-state-area>
                    <state>MD</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

            </tax-rules>
          </default-tax-table>

          <alternate-tax-tables>
            <alternate-tax-table standalone="false" name="bicycle_helmets">
              <alternate-tax-rules>
                <alternate-tax-rule>
                  <rate>0</rate>
                  <tax-area>
                    <us-state-area>
                      <state>CT</state>
                    </us-state-area>
                  </tax-area>
                </alternate-tax-rule>
              </alternate-tax-rules>
            </alternate-tax-table>
          </alternate-tax-tables>

        </tax-tables>
      </merchant-checkout-flow-support>
    </checkout-flow-support>


Python:

.. code-block:: python

    >>> gc.add_fields({'items': [{
      "amount": 49.99,
      "name": "Bike Helmet",
      "description": "Black helmet that is tax-exempt in CT but not MD.",
      "currency": "USD",
      "id": "item_id",
      "quantity": 1,
      "tax-table-selector": "bicycle_helmets"
      }],
      'tax-tables': {
                'default-tax-table': {
                        'tax-rules': [
                            {
                                'shipping-taxed': True,
                                'rate': 0.06,
                                'tax-area': {
                                    'us-state-area': ['CT'],
                                 }
                            },
                            {
                                'rate': 0.05,
                                'tax-area': {
                                    'us-state-area': ['MD'],
                                 }
                            }
                        ]
                    },
                'alternate-tax-tables': [
                    {'name': 'bicycle_helmets',
                     'standalone': False,
                     'alternative-tax-rules': [
                        { 'rate': 0,
                          'tax-area': {
                            'us-state-area': ['CT'],
                          }
                        }
                      ]
                    }
                  ]
        })


Example 5: Alternate tax rules for items that are always tax-exempt
*******************************************************************
This example shows how to identify an item that is always tax-exempt, regardless of the shipping address. The tax tables indicate that the merchant charges sales tax in Connecticut and Maryland, and sales of nonprescription drugs are tax-exempt in both states. In this example, the XML contains an alternate tax table for tax-exempt goods, and that tax table does not specify any alternate tax rules. However, since the value of the <alternate-tax-table> tag's standalone attribute is set to true, Google will not calculate taxes for an item if it specifies the tax-exempt tax table and there is no alternate tax rule for the shipping address. Since the item in the example is always tax-exempt for this merchant, the tax table does not need to specify any tax rules.


XML:

.. code-block:: xml

    <shopping-cart>
      <items>
        <item>
          <item-name>Tylenol Caplets</item-name>
          <item-description>Fast relief without a prescription.</item-description>
          <unit-price currency="USD">7.99</unit-price>
          <quantity>1</quantity>
          <tax-table-selector>tax_exempt</tax-table-selector>
        </item>
      </items>
    </shopping-cart>
    <checkout-flow-support>
      <merchant-checkout-flow-support>
        <tax-tables>
          <default-tax-table>
            <tax-rules>

              <default-tax-rule>
                <shipping-taxed>true</shipping-taxed>
                <rate>0.0600</rate>
                <tax-area>
                  <us-state-area>
                    <state>CT</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

              <default-tax-rule>
                <rate>0.0500</rate>
                <tax-area>
                  <us-state-area>
                    <state>MD</state>
                  </us-state-area>
                </tax-area>
              </default-tax-rule>

            </tax-rules>
          </default-tax-table>

          <alternate-tax-tables>
            <alternate-tax-table standalone="true" name="tax_exempt">
              <alternate-tax-rules/>
            </alternate-tax-table>
          </alternate-tax-tables>
        </tax-tables>
      </merchant-checkout-flow-support>
    </checkout-flow-support>


Python:

.. code-block:: python

    >>> gc.add_fields({'items': [{
      "amount": 7.99,
      "name": "Tylenol Caplets",
      "description": "Fast relief without a prescription.",
      "currency": "USD",
      "id": "item_id",
      "quantity": 1,
      "tax-table-selector": "tax_exempt"
      }],
      'tax-tables': {
                'default-tax-table': {
                        'tax-rules': [
                            {
                                'shipping-taxed': True,
                                'rate': 0.06,
                                'tax-area': {
                                    'us-state-area': ['CT'],
                                 }
                            },
                            {
                                'rate': 0.05,
                                'tax-area': {
                                    'us-state-area': ['MD'],
                                 }
                            }
                        ]
                    },
                'alternate-tax-tables': [
                    {'name': 'tax_exempt',
                     'standalone': True,
                    }
                ]
        })


Example 6: Applying a tax rule in multiple geographic areas
***********************************************************
This example demonstrates how to use the <tax-areas> tag to apply a tax rule in multiple geographic areas. This example applies the same tax rule in multiple European countries. The same principle could be used to apply a tax rule in multiple U.S. states or zip code ranges.

XML:

.. code-block:: xml

        <tax-tables>
          <default-tax-table>
            <tax-rules>

              <default-tax-rule>
                <shipping-taxed>true</shipping-taxed>
                <rate>0.175</rate>
                <tax-areas>
                  <postal-area>
                    <country-code>DE</country-code>
                  </postal-area>
                  <postal-area>
                    <country-code>ES</country-code>
                  </postal-area>
                  <postal-area>
                    <country-code>GB</country-code>
                  </postal-area>
                </tax-areas>
              </default-tax-rule>

            </tax-rules>
          </default-tax-table>
        </tax-tables>

Python:

.. code-block:: python

        >>> gc.add_fields({'items': ... ,
            'tax-tables': {
                'default-tax-table': {
                        'tax-rules': [
                            {
                                'shipping-taxed': True,
                                'rate': 0.175,
                                'tax-area': {
                                    'postal-area': [
                                        {'country-code': 'DE'},
                                        {'country-code': 'ES'},
                                        {'country-code': 'GB'},
                                    ],
                                 },
                            },
                        ]
                    },
                }
            })


Example 7: Alternate tax tables for U.K. merchants
**************************************************
This example shows a common way to structure tax tables in the United Kingdom. The order includes three items. The first item uses the default tax rate of 17.5 percent, the second item uses a reduced tax rate of 5 percent, and the third item is untaxed. Note that the cost of each item is £10.00. When you click the Checkout button for this order, Google Checkout displays the price for each item inclusive of tax.


XML:

.. code-block:: xml

    <shopping-cart>
      <items>
        <item>
          <item-name>Regular Test Item</item-name>
          <item-description>Regular Test Item</item-description>
          <unit-price currency="GBP">10.0</unit-price>
          <quantity>1</quantity>
        </item>
        <item>
          <item-name>Reduced Test Item</item-name>
          <item-description>Reduced Test Item</item-description>
          <unit-price currency="GBP">10.0</unit-price>
          <quantity>1</quantity>
          <tax-table-selector>reduced</tax-table-selector>
        </item>
        <item>
          <item-name>Zero Test Item</item-name>
          <item-description>Zero Test Item</item-description>
          <unit-price currency="GBP">10.0</unit-price>
          <quantity>1</quantity>
          <tax-table-selector>tax_exempt</tax-table-selector>
        </item>
      </items>
    </shopping-cart>
    <checkout-flow-support>
      <merchant-checkout-flow-support>
        <tax-tables>
          <default-tax-table>
            <tax-rules>

              <default-tax-rule>
                <shipping-taxed>true</shipping-taxed>
                <rate>0.175</rate>
                <tax-area>
                  <world-area/>
                </tax-area>
              </default-tax-rule>

            </tax-rules>
          </default-tax-table>

          <alternate-tax-tables>
            <alternate-tax-table name="reduced" standalone="true">
              <alternate-tax-rules>
                <alternate-tax-rule>
                  <rate>0.05</rate>
                  <tax-area>
                    <world-area/>
                  </tax-area>
                </alternate-tax-rule>
              </alternate-tax-rules>
            </alternate-tax-table>

            <alternate-tax-table standalone="true" name="tax_exempt">
              <alternate-tax-rules/>
            </alternate-tax-table>
          </alternate-tax-tables>

        </tax-tables>
      </merchant-checkout-flow-support>
    </checkout-flow-support>

Python:

.. code-block:: python

    >>> gc.add_fields({'items': [{
      "amount": 10.0,
      "name": "Regular Test Item",
      "description": "Regular Test Item",
      "currency": "GBP",
      "quantity": 1,
      },{
      "amount": 10.0,
      "name": "Reduced Test Item",
      "description": "Reduced Test Item",
      "currency": "GBP",
      "quantity": 1,
      "tax-table-selector": "reduced"
      },{
      "amount": 10.0,
      "name": "Zero Test Item",
      "description": "Zero Test Item",
      "currency": "GBP",
      "quantity": 1,
      "tax-table-selector": "tax_exempt"
      }],
      'tax-tables': {
                'default-tax-table': {
                        'tax-rules': [
                            {
                                'shipping-taxed': True,
                                'rate': 0.175,
                                'tax-area': {
                                    'world-area': True,
                                 },
                            },
                        ]
                    },
                'alternate-tax-tables': [
                    {'name': 'reduced',
                     'standalone': True,
                     'alternative-tax-rules': [
                        { 'rate': 0.05,
                          'tax-area': {
                            'world-area': True,
                          }
                        },
                      ]
                     },
                    { 'name': 'tax_exempt',
                     'standalone': True,
                    }
                ]
        })


Shipping:
---------
The following shipping methods are supported: flat-rate-shipping, merchant-calculated-shipping, pickup. carrier-calculated-shipping is not supported yet.

Flat-rate shipping + Pickup
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here are the examples from the `Google Checkouts Developer Docs <https://developers.google.com/checkout/developer/Google_Checkout_XML_API_Flat_Rate_Shipping>`_ converted to django-merchant.

These are only showing the shipping methods section, you still need items and everything else.

Example 1 - Using Flat-rate Shipping:
*************************************
The following example shows two flat-rate shipping methods. The first shipping method, which is for UPS Next Day Air shipping, costs $20.00. The second option, which is for UPS Ground Shipping, costs $15.00.

XML:

.. code-block:: xml

      <shipping-methods>
        <flat-rate-shipping name="UPS Next Day Air">
          <price currency="USD">20.00</price>
        </flat-rate-shipping>
        <flat-rate-shipping name="UPS Ground">
          <price currency="USD">15.00</price>
        </flat-rate-shipping>
      </shipping-methods>

Python:

.. code-block:: python

    >>> gc.add_fields({'items': ... ,
        'shipping-methods': [
            {'shipping_type':'flat-rate-shipping',
             'name':"UPS Next Day Air",
             'currency':"USD",
             'price':20.00},
            {'shipping_type':'flat-rate-shipping',
             'name':"UPS Ground",
             'currency':"USD",
             'price':15.00},
        ]})

Example 2 - Using Shipping Restrictions:
****************************************
In this example, the merchant offers the same two shipping options as in example 1. However, in this example, the merchant has added shipping restrictions to both shipping methods. These restrictions specify that neither option will be offered if the shipping address is a P.O. box. In addition, the next-day shipping option will also be unavailable if the shipping address is in either Alaska or Hawaii.

The following list explains how Google Checkout will handle different shipping addresses based on the XML in the example:

- Google Checkout will not allow the buyer to complete the order if the selected shipping address is a P.O. box.

- If the buyer selects a shipping address in Alaska or Hawaii (that is not a P.O. box), then Google Checkout will only offer the second shipping option (for ground shipping) to the buyer.

- If the buyer selects any shipping address that is not a P.O. box and is not in Alaska or Hawaii, then Google Checkout will offer both shipping options to the buyer.

XML:

.. code-block:: xml

    <shipping-methods>
        <flat-rate-shipping name="UPS Next Day Air">
          <price currency="USD">20.00</price>
          <shipping-restrictions>
            <excluded-areas>
              <us-state-area>
                <state>AK</state>
              </us-state-area>
              <us-state-area>
                <state>HI</state>
              </us-state-area>
            </excluded-areas>
            <allow-us-po-box>false</allow-us-po-box>
          </shipping-restrictions>
        </flat-rate-shipping>
        
        <flat-rate-shipping name="UPS Ground">
          <price currency="USD">15.00</price>
          <shipping-restrictions>
            <allow-us-po-box>false</allow-us-po-box>
          </shipping-restrictions>
        </flat-rate-shipping>
    </shipping-methods>


Python:

.. code-block:: python

    >>> gc.add_fields({'items': ... ,
        'shipping-methods': [
            {'shipping_type':'flat-rate-shipping',
             'name':"UPS Next Day Air",
             'currency':"USD",
             'price':20.00,
             'shipping-restrictions': {
                'allow-us-po-box': False,
                'excluded-areas': {
                        'us-state-area' : ['AK', 'HI']
                        }
                }
             },
            {'shipping_type':'flat-rate-shipping',
             'name':"UPS Ground",
             'currency':"USD",
             'price':15.00,
             'shipping-restrictions': {
                'allow-us-po-box': False,
                }
            },
        ]})


Example 3 - Offering Delivery or Pickup with Flat-Rate Shipping Options:
************************************************************************
This example demonstrates how you could offer free delivery using a flat-rate shipping method. The example also includes a <pickup> shipping method. In this example, the request uses shipping restrictions to specify that delivery is only available in two zip codes in Manhattan's Upper East Side neighborhood. You can charge a fee for delivery by setting the value of the <price> tag to the delivery fee amount.

XML:

.. code-block:: xml

    <shipping-methods>
        <flat-rate-shipping name="Delivery">
          <price currency="USD">0.00</price>
          <shipping-restrictions>
            <allowed-areas>
              <us-zip-area>
                <zip-pattern>10021</zip-pattern>
              </us-zip-area>
              <us-zip-area>
                <zip-pattern>10022</zip-pattern>
              </us-zip-area>
            </allowed-areas>
            <allow-us-po-box>false</allow-us-po-box>
          </shipping-restrictions>
        </flat-rate-shipping>
        
        <pickup name="Pickup">
          <price currency="USD">0.00</price>
        </pickup>
      </shipping-methods>


Python:

.. code-block:: python

    >>> gc.add_fields({'items': ... ,
        'shipping-methods': [
            {'shipping_type':'flat-rate-shipping',
             'name':"Delivery",
             'currency':"USD",
             'price':0.00,
             'shipping-restrictions': {
                'allow-us-po-box': False,
                'allowed-areas': {
                        'us-zip-area' : [10021, 10022]
                        }
                }
             },
            {'shipping_type':'pickup',
             'name':"Pickup",
             'currency':"USD",
             'price':0.00,
            },
        ]})

Merchant-calculated Shipping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here are the examples from the `Google Checkouts Developer Docs <https://developers.google.com/checkout/developer/Google_Checkout_XML_API_Merchant_Calculated_Shipping>`_ converted to django-merchant.

These are only showing the shipping methods section, you still need items and everything else.


Example 1 - Using Merchant Calculated Shipping
**********************************************
The following example shows an order for a U.S. merchant with one item and two merchant-calculated shipping methods. The first shipping method, which is for UPS Next Day Air shipping, has a default price of $20.00. This option also will not be offered if the shipping address is a P.O. box in the United States. The second option, which is for UPS Ground Shipping, has a default price of $15.00. The example also specifies that the merchant will calculate taxes as well as price adjustments associated with coupons or gift certificates.

XML:

.. code-block:: xml

    <shipping-methods>

        <merchant-calculated-shipping name="UPS Next Day Air">
          <price currency="USD">20.00</price>
          <address-filters>
            <allow-us-po-box>false<allow-us-po-box>
          </address-filters>
        </merchant-calculated-shipping>

        <merchant-calculated-shipping name="UPS Ground">
          <price currency="USD">15.00</price>
        </merchant-calculated-shipping>

      </shipping-methods>
      
Python:

.. code-block:: python

    >>> gc.add_fields({'items': ... ,
    'shipping-methods': [
        {'shipping_type':'merchant-calculated-shipping',
         'name':"UPS Next Day Air",
         'currency':"USD",
         'price':20.00,
         'address-filters': {
            'allow-us-po-box': False,
            }
         },
        {'shipping_type':'merchant-calculated-shipping',
         'name':"UPS Ground",
         'currency':"USD",
         'price':15.00,
        },
    ]})


Example 2 - Using Address Filters and Shipping Restrictions:
************************************************************
In this example, the merchant offers the same two shipping options as in example 1. However, in this example, the merchant has added shipping restrictions to specify that the next-day shipping option will not be available if the <merchant-calculation-callback> request fails and the shipping address is in either Alaska or Hawaii.

The following list explains how Google Checkout will handle different shipping addresses based on the XML in the example:

- If the customer enters any U.S. postal address that is not a P.O. box, Google Checkout will send a callback request instructing the merchant to calculate shipping costs for both shipping options.

    - If the callback request is successful, then Google will offer the two shipping options to the buyer using the shipping costs from the merchant's <merchant-calculation-response>.

    - If the callback request is not successful, and the shipping address is in the continental United States, Google will let the buyer choose either of the two shipping methods. In this case, the next-day shipping method will cost $20.00 and the ground shipping method will cost $15.00.

    - If the callback request is not successful, and the shipping address is in Alaska or Hawaii, Google will only offer the second shipping option at a cost of $15.00.

- If the customer enters a U.S. postal address that is a P.O. box, Google Checkout will send a callback request instructing the merchant to calculate the shipping cost for the second shipping option, which is for ground shipping. Since the address filter for the first shipping option indicates that that option is not available for P.O. boxes, Google will not allow the customer to select that shipping option and will not ask the merchant to calculate the cost of that shipping option.

XML:

.. code-block:: xml

    <shipping-methods>

        <merchant-calculated-shipping name="UPS Next Day Air">
          <price currency="USD">20.00</price>
          <address-filters>
            <allow-us-po-box>false<allow-us-po-box>
          </address-filters>
          <shipping-restrictions>
            <excluded-areas>
              <us-state-area>
                <state>AK</state>
              </us-state-area>
              <us-state-area>
                <state>HI</state>
              </us-state-area>
            </excluded-areas>
          </shipping-restrictions>
        </merchant-calculated-shipping>

        <merchant-calculated-shipping name="UPS Ground">
          <price currency="USD">15.00</price>
        </merchant-calculated-shipping>

      </shipping-methods>

Python:

.. code-block:: python

    >>> gc.add_fields({'items': ... ,
    'shipping-methods': [
        {'shipping_type':'merchant-calculated-shipping',
         'name':"UPS Next Day Air",
         'currency':"USD",
         'price':20.00,
         'address-filters': {
            'allow-us-po-box': False,
            }
         },
         'shipping-restrictions': {
            'allow-us-po-box': False,
            'excluded-areas': {
                    'us-state-area' : ['AK', 'HI']
                    }
            }
         },
        {'shipping_type':'merchant-calculated-shipping',
         'name':"UPS Ground",
         'currency':"USD",
         'price':15.00,
        },
    ]})


.. _`Google Checkout`: https://checkout.google.com/
.. _here: http://code.google.com/apis/checkout/
.. _`Merchant Center`: http://code.google.com/apis/checkout/developer/Google_Checkout_Glossary.html#merchant_center
