from xml.dom.minidom import Document, parseString

from django.conf import settings
from django.test import TestCase
from django.template import Template, Context

from billing import get_integration
from django.utils.unittest.case import skipIf


@skipIf(not settings.MERCHANT_SETTINGS.get("google_checkout", None), "gateway not configured")
class GoogleCheckoutTestCase(TestCase):
    def setUp(self):
        self.gc = get_integration("google_checkout")
        target_url_name = "example.com/offsite/my_content/"
        target_url = 'http://' + target_url_name
        fields = {
            "items": [
                {
                    "name": "name of the item",
                    "description": "Item description",
                    "amount": 0.00,
                    "id": "999AXZ",
                    "currency": "USD",
                    "quantity": 1,
                    "subscription": {
                        "type": "merchant",                     # valid choices is ["merchant", "google"]
                        "period": "YEARLY",                     # valid choices is ["DAILY", "WEEKLY", "SEMI_MONTHLY", "MONTHLY", "EVERY_TWO_MONTHS"," QUARTERLY", "YEARLY"]
                        "payments": [
                            {
                                "maximum-charge": 9.99,         # Item amount must be "0.00"
                                "currency": "USD"
                            }
                        ]
                    },
                    "digital-content": {
                        "display-disposition": "OPTIMISTIC",    # valid choices is ['OPTIMISTIC', 'PESSIMISTIC']
                        "description": "Congratulations! Your subscription is being set up. Feel free to log onto &amp;lt;a href='%s'&amp;gt;%s&amp;lt;/a&amp;gt; and try it out!" % (target_url, target_url_name)
                    },
                },
            ],
            "return_url": "http://127.0.0.1:8000/offsite/google-checkout/",
            'private_data': "test@example.com",
         }
        self.gc.add_fields(fields)

    def testFormGen(self):
        tmpl = Template("{% load render_integration from billing_tags %}{% render_integration obj %}")
        form = tmpl.render(Context({"obj": self.gc}))

        dom = parseString(form)
        form_action_url = dom.getElementsByTagName('form')[0].attributes['action'].value
        input_image_src = dom.getElementsByTagName('input')[2].attributes['src'].value

        expected_form_action_url = "https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/%s" % settings.MERCHANT_SETTINGS['google_checkout']['MERCHANT_ID']
        expected_input_image_src = "https://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=%s&w=180&h=46&style=white&variant=text&loc=en_US" % settings.MERCHANT_SETTINGS['google_checkout']['MERCHANT_ID']

        self.assertEquals(form_action_url, expected_form_action_url)
        self.assertEquals(input_image_src, expected_input_image_src)


    def testBuildXML(self):
        xml = self.gc.build_xml()
        good_xml = """<?xml version="1.0" encoding="utf-8"?><checkout-shopping-cart xmlns="http://checkout.google.com/schema/2"><shopping-cart><items><item><item-name>name of the item</item-name><item-description>Item description</item-description><unit-price currency="USD">0.0</unit-price><quantity>1</quantity><merchant-item-id>999AXZ</merchant-item-id><subscription period="YEARLY" type="merchant"><payments><subscription-payment><maximum-charge currency="USD">9.99</maximum-charge></subscription-payment></payments></subscription><digital-content><display-disposition>OPTIMISTIC</display-disposition><description>Congratulations! Your subscription is being set up. Feel free to log onto &amp;amp;lt;a href=\'http://example.com/offsite/my_content/\'&amp;amp;gt;example.com/offsite/my_content/&amp;amp;lt;/a&amp;amp;gt; and try it out!</description></digital-content></item></items><merchant-private-data>test@example.com</merchant-private-data></shopping-cart><checkout-flow-support><merchant-checkout-flow-support><continue-shopping-url>http://127.0.0.1:8000/offsite/google-checkout/</continue-shopping-url></merchant-checkout-flow-support></checkout-flow-support></checkout-shopping-cart>"""
        self.assertEquals(xml, good_xml)

@skipIf(not settings.MERCHANT_SETTINGS.get("google_checkout", None), "gateway not configured")
class GoogleCheckoutShippingTestCase(TestCase):
    def setUp(self):
        self.gc = get_integration("google_checkout")
        self.maxDiff = None

    def testAddNodes(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        child_node_values = ['child1', 'child2', 'child3']
        self.gc._add_nodes(doc, parent_node, 'child_node','child_sub_node', child_node_values)
        xml1 = "<parent_node><child_node><child_sub_node>child1</child_sub_node></child_node>\
<child_node><child_sub_node>child2</child_sub_node></child_node>\
<child_node><child_sub_node>child3</child_sub_node></child_node></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testAddNodes_novalues(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        child_node_values = []
        self.gc._add_nodes(doc, parent_node, 'child_node','child_sub_node', child_node_values)
        xml1 = """<parent_node></parent_node>"""
        doc_good = parseString(xml1)
        self.assertEquals(doc.toprettyxml(), doc_good.toprettyxml())

    def testShippingExclude(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
            'us-state-area': ['AK','HI'],
            'us-zip-area': ['90210', '04005', '04092'],
            'us-country-area': 'CONTINENTAL_48',
            'world-area': True,
            'postal-area': [{
                'country-code': 'US',
                'postal-code-pattern': ['94043', '90211'],
                },
            ],
        }
        self.gc._shipping_allowed_excluded(doc, parent_node, data)
        xml1 = "<parent_node><us-state-area><state>AK</state></us-state-area>\
<us-state-area><state>HI</state></us-state-area>\
<us-zip-area><zip-pattern>90210</zip-pattern></us-zip-area>\
<us-zip-area><zip-pattern>04005</zip-pattern></us-zip-area>\
<us-zip-area><zip-pattern>04092</zip-pattern></us-zip-area>\
<us-country-area country-area='CONTINENTAL_48'/>\
<world-area/>\
<postal-area><country-code>US</country-code>\
<postal-code-pattern>94043</postal-code-pattern>\
<postal-code-pattern>90211</postal-code-pattern></postal-area>\
</parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testShippingRestrictions(self):
        """ Not a real data since you would never put the these values for
            exclude and include, but wanted to test everything on both sides
            should work the same for both allowed and excluded"""
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
            'allowed-areas': {
                'us-state-area': ['ME','NH'],
                'us-zip-area': ['04005', '04092'],
                'us-country-area': 'ALL',
                'world-area': True,
                'postal-area': [{
                    'country-code': 'US',
                    'postal-code-pattern': ['94043', '90211'],
                    },
                ],
            },
            'excluded-areas': {
                'us-state-area': ['AK','HI'],
                'us-zip-area': ['90210'],
                'us-country-area': 'CONTINENTAL_48',
                'world-area': False,
                'postal-area': [{
                    'country-code': 'US',
                    'postal-code-pattern': ['11111', '11112'],
                    },
                ],
            },
        }
        self.gc._shipping_restrictions_filters(doc, parent_node, data)
        xml1 = "<parent_node><allowed-areas><us-state-area>\
<state>ME</state></us-state-area>\
<us-state-area><state>NH</state></us-state-area>\
<us-zip-area><zip-pattern>04005</zip-pattern></us-zip-area>\
<us-zip-area><zip-pattern>04092</zip-pattern></us-zip-area>\
<us-country-area country-area='ALL'/>\
<world-area/>\
<postal-area><country-code>US</country-code>\
<postal-code-pattern>94043</postal-code-pattern>\
<postal-code-pattern>90211</postal-code-pattern></postal-area>\
</allowed-areas>\
<excluded-areas><us-state-area><state>AK</state></us-state-area>\
<us-state-area><state>HI</state></us-state-area>\
<us-zip-area><zip-pattern>90210</zip-pattern></us-zip-area>\
<us-country-area country-area='CONTINENTAL_48'/>\
<postal-area><country-code>US</country-code>\
<postal-code-pattern>11111</postal-code-pattern>\
<postal-code-pattern>11112</postal-code-pattern></postal-area>\
</excluded-areas></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testFullCartXML(self):
        fields = {"items": [{
            "name": "name of the item",
            "description": "Item description",
            "amount": 1,
            "id": "999AXZ",
            "currency": "USD",
            "quantity": 1,
            }],
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
        ],
       "return_url": "http://127.0.0.1:8000/offsite/google-checkout/",
       }
        self.gc.add_fields(fields)

        xml = self.gc.build_xml()
        good_xml = """<?xml version="1.0" encoding="utf-8"?><checkout-shopping-cart xmlns="http://checkout.google.com/schema/2"><shopping-cart><items><item><item-name>name of the item</item-name><item-description>Item description</item-description><unit-price currency="USD">1</unit-price><quantity>1</quantity><merchant-item-id>999AXZ</merchant-item-id></item></items><merchant-private-data></merchant-private-data></shopping-cart><checkout-flow-support><merchant-checkout-flow-support><continue-shopping-url>http://127.0.0.1:8000/offsite/google-checkout/</continue-shopping-url><shipping-methods><flat-rate-shipping name="UPS Next Day Air"><price currency="USD">20.0</price><shipping-restrictions><allow-us-po-box>false</allow-us-po-box><excluded-areas><us-state-area><state>AK</state></us-state-area><us-state-area><state>HI</state></us-state-area></excluded-areas></shipping-restrictions></flat-rate-shipping><flat-rate-shipping name="UPS Ground"><price currency="USD">15.0</price><shipping-restrictions><allow-us-po-box>false</allow-us-po-box></shipping-restrictions></flat-rate-shipping></shipping-methods></merchant-checkout-flow-support></checkout-flow-support></checkout-shopping-cart>"""
        self.assertEquals(xml, good_xml)


@skipIf(not settings.MERCHANT_SETTINGS.get("google_checkout", None), "gateway not configured")
class GoogleCheckoutTaxTestCase(TestCase):
    """ Test the tax code """

    def setUp(self):
        self.gc = get_integration("google_checkout")
        self.maxDiff = None

    def testTaxes1(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
                'default-tax-table': {
                    'tax-rules': [
                        {
                            'shipping-taxed': True,
                            'rate': 0.06,
                            'tax-area': {
                                'us-state-area': ['CT'],
                             }
                        }
                    ]
                }
        }
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables><default-tax-table><tax-rules>\
<default-tax-rule><shipping-taxed>true</shipping-taxed><rate>0.06</rate>\
<tax-area><us-state-area><state>CT</state></us-state-area></tax-area>\
</default-tax-rule></tax-rules></default-tax-table></tax-tables>\
</parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testTaxes2(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
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
                    }
        }
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables><default-tax-table><tax-rules>\
<default-tax-rule><shipping-taxed>true</shipping-taxed><rate>0.06</rate>\
<tax-area><us-state-area><state>CT</state></us-state-area></tax-area>\
</default-tax-rule><default-tax-rule><shipping-taxed>false</shipping-taxed>\
<rate>0.05</rate><tax-area><us-state-area><state>MD</state></us-state-area>\
</tax-area></default-tax-rule></tax-rules></default-tax-table></tax-tables>\
</parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testTaxes3(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
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
                                'rate': 0.04,
                                'tax-area': {
                                    'us-state-area': ['NY'],
                                 }
                            }
                        ]
                    }
        }
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables><default-tax-table>\
<tax-rules><default-tax-rule><shipping-taxed>false</shipping-taxed>\
<rate>0.08375</rate><tax-area><us-zip-area><zip-pattern>100*</zip-pattern>\
</us-zip-area></tax-area></default-tax-rule>\
<default-tax-rule><shipping-taxed>true</shipping-taxed>\
<rate>0.04</rate><tax-area><us-state-area><state>NY</state></us-state-area>\
</tax-area></default-tax-rule>\
</tax-rules></default-tax-table></tax-tables></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testTaxes4(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
                'default-tax-table': {
                        'tax-rules': [
                            {
                                'shipping-taxed': False,
                                'rate': 0.08375,
                                'tax-area': {
                                    'us-zip-area': ['100*', '040*'],
                                 }
                            },
                            {
                                'shipping-taxed': True,
                                'rate': 0.04,
                                'tax-area': {
                                    'us-state-area': ['NY', 'ME'],
                                 }
                            }
                        ]
                    }
        }
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables><default-tax-table>\
<tax-rules><default-tax-rule><shipping-taxed>false</shipping-taxed>\
<rate>0.08375</rate><tax-areas><us-zip-area><zip-pattern>100*</zip-pattern>\
</us-zip-area><us-zip-area><zip-pattern>040*</zip-pattern>\
</us-zip-area></tax-areas></default-tax-rule>\
<default-tax-rule><shipping-taxed>true</shipping-taxed>\
<rate>0.04</rate><tax-areas><us-state-area><state>NY</state></us-state-area>\
<us-state-area><state>ME</state></us-state-area>\
</tax-areas></default-tax-rule>\
</tax-rules></default-tax-table></tax-tables></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testTaxes5(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
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
        }
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables>\
<default-tax-table><tax-rules><default-tax-rule>\
<shipping-taxed>true</shipping-taxed><rate>0.06</rate>\
<tax-area><us-state-area><state>CT</state></us-state-area>\
</tax-area></default-tax-rule><default-tax-rule>\
<shipping-taxed>false</shipping-taxed><rate>0.05</rate>\
<tax-area><us-state-area><state>MD</state></us-state-area>\
</tax-area></default-tax-rule></tax-rules></default-tax-table>\
<alternate-tax-tables><alternate-tax-table name='bicycle_helmets' standalone='false'>\
<alternate-tax-rules><alternate-tax-rule><rate>0</rate>\
<tax-area><us-state-area><state>CT</state></us-state-area></tax-area>\
</alternate-tax-rule></alternate-tax-rules></alternate-tax-table>\
</alternate-tax-tables></tax-tables></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testTaxes6(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
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
        }
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables>\
<default-tax-table><tax-rules><default-tax-rule>\
<shipping-taxed>true</shipping-taxed><rate>0.06</rate>\
<tax-area><us-state-area><state>CT</state></us-state-area>\
</tax-area></default-tax-rule><default-tax-rule>\
<shipping-taxed>false</shipping-taxed><rate>0.05</rate>\
<tax-area><us-state-area><state>MD</state></us-state-area>\
</tax-area></default-tax-rule></tax-rules></default-tax-table>\
<alternate-tax-tables><alternate-tax-table name='tax_exempt' standalone='true'>\
<alternate-tax-rules/></alternate-tax-table>\
</alternate-tax-tables></tax-tables></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testTaxes7(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
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
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables>\
<default-tax-table><tax-rules><default-tax-rule>\
<shipping-taxed>true</shipping-taxed><rate>0.175</rate>\
<tax-areas><postal-area><country-code>DE</country-code>\
</postal-area><postal-area><country-code>ES</country-code>\
</postal-area><postal-area><country-code>GB</country-code>\
</postal-area></tax-areas></default-tax-rule></tax-rules>\
</default-tax-table></tax-tables></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())

    def testTaxes8(self):
        doc = Document()
        parent_node = doc.createElement('parent_node')
        doc.appendChild(parent_node)
        data = {
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
        }
        self.gc._taxes(doc, parent_node, data)
        xml1 = "<parent_node><tax-tables>\
<default-tax-table><tax-rules>\
<default-tax-rule><shipping-taxed>true</shipping-taxed>\
<rate>0.175</rate><tax-area><world-area/></tax-area>\
</default-tax-rule></tax-rules></default-tax-table>\
<alternate-tax-tables><alternate-tax-table name='reduced' standalone='true'>\
<alternate-tax-rules><alternate-tax-rule><rate>0.05</rate><tax-area>\
<world-area/></tax-area></alternate-tax-rule></alternate-tax-rules>\
</alternate-tax-table><alternate-tax-table standalone='true' name='tax_exempt'>\
<alternate-tax-rules/></alternate-tax-table></alternate-tax-tables>\
</tax-tables></parent_node>"
        doc_good = parseString(xml1)
        self.assertEquals(doc.toxml(), doc_good.toxml())


    def testFullCartXML(self):
        fields = {"items": [{
            "name": "name of the item",
            "description": "Item description",
            "amount": 1,
            "id": "999AXZ",
            "currency": "USD",
            "quantity": 1,
            },
            {
            "name": "tax free item",
            "description": "Item description",
            "amount": 2,
            "id": "999AXZ",
            "currency": "USD",
            "quantity": 1,
            "tax-table-selector": 'tax_exempt',
            },
            ],
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
                            'rate': 0.04,
                            'tax-area': {
                                'us-state-area': ['NY'],
                             }
                        }
                    ]
                },
                'alternate-tax-tables': [
                    {
                     'name': 'tax_exempt',
                     'standalone': True,
                    }
                ]
           },
           "return_url": "http://127.0.0.1:8000/offsite/google-checkout/",
           }
        self.gc.add_fields(fields)

        xml = self.gc.build_xml()
        good_xml = """<?xml version="1.0" encoding="utf-8"?><checkout-shopping-cart xmlns="http://checkout.google.com/schema/2"><shopping-cart><items><item><item-name>name of the item</item-name><item-description>Item description</item-description><unit-price currency="USD">1</unit-price><quantity>1</quantity><merchant-item-id>999AXZ</merchant-item-id></item><item><item-name>tax free item</item-name><item-description>Item description</item-description><unit-price currency="USD">2</unit-price><quantity>1</quantity><merchant-item-id>999AXZ</merchant-item-id><tax-table-selector>tax_exempt</tax-table-selector></item></items><merchant-private-data></merchant-private-data></shopping-cart><checkout-flow-support><merchant-checkout-flow-support><continue-shopping-url>http://127.0.0.1:8000/offsite/google-checkout/</continue-shopping-url><tax-tables><default-tax-table><tax-rules><default-tax-rule><shipping-taxed>false</shipping-taxed><rate>0.08375</rate><tax-area><us-zip-area><zip-pattern>100*</zip-pattern></us-zip-area></tax-area></default-tax-rule><default-tax-rule><shipping-taxed>true</shipping-taxed><rate>0.04</rate><tax-area><us-state-area><state>NY</state></us-state-area></tax-area></default-tax-rule></tax-rules></default-tax-table><alternate-tax-tables><alternate-tax-table name="tax_exempt" standalone="true"><alternate-tax-rules/></alternate-tax-table></alternate-tax-tables></tax-tables></merchant-checkout-flow-support></checkout-flow-support></checkout-shopping-cart>"""
        self.assertEquals(xml, good_xml)
