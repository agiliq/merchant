# -*- coding: utf-8 -*-
import random
import sys
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.utils.unittest import skipIf

from billing.tests.utils import BetterXMLCompareMixin
from billing.gateway import get_gateway
from billing.gateways.global_iris_gateway import GlobalIrisGateway, CARD_NAMES
from billing.integrations.global_iris_real_mpi_integration import GlobalIrisRealMpiIntegration
from billing.signals import transaction_was_unsuccessful, transaction_was_successful
from billing.utils.credit_card import CreditCard, CardNotSupported, Visa


class Dummy200Response(object):
    def __init__(self, content):
        self.status_code = 200
        self.content = content


class GlobalIrisTestBase(object):

    def mk_gateway(self):
        return GlobalIrisGateway(
            config={'TEST': dict(SHARED_SECRET="mysecret",
                                 MERCHANT_ID="thestore",
                                 ACCOUNT="theaccount")
                    },
            test_mode=True)

    def mk_integration(self):
        return GlobalIrisRealMpiIntegration(
            config={'TEST': dict(SHARED_SECRET="mysecret",
                                 MERCHANT_ID="thestore",
                                 ACCOUNT="theaccount")
                    },
            test_mode=True)

    def get_visa_card(self):
        return CreditCard(first_name='Mickey',
                          last_name='Mouse',
                          month=7,
                          year=2035,
                          number='4903034000057389',
                          verification_value='123',
                          )

    def get_amex_card(self):
        return CreditCard(first_name='Donald',
                          last_name='Duck',
                          month=8,
                          year=2035,
                          number='374101012180018',
                          verification_value='4567',
                          )

    def get_order_id(self):
        # Need unique IDs for orders
        return str(datetime.now()).replace(':', '_').replace(' ', '_').replace('.', '_') + str(random.randint(0, sys.maxint))


@skipIf(not settings.MERCHANT_SETTINGS.get("global_iris", None), "gateway not configured")
class GlobalIrisGatewayTestCase(BetterXMLCompareMixin, GlobalIrisTestBase, TestCase):

    def test_request_xml(self):
        gateway = self.mk_gateway()
        card = CreditCard(first_name='Mickey',
                          last_name='Mouse',
                          month=7,
                          year=2014,
                          number='4903034000057389',
                          verification_value='123',
                          )
        gateway.validate_card(card)
        data = {
                'timestamp': datetime(2001, 4, 27, 12, 45, 23),
                'order_id': '345',
                'amount': Decimal('20.00'),
                'card': card,
                'customer': '567',
                'billing_address': {
                    'street_address': "45 The Way",
                    'post_code': "ABC 123",
                    'country': 'GB',
                    },
                'product_id': '678',
                'customer_ip_address': '123.4.6.23',
                'varref': 'abc',
                }

        xml = gateway.build_xml(data)

        self.assertXMLEqual(u"""<?xml version="1.0" encoding="UTF-8" ?>
<request timestamp="20010427124523" type="auth">
  <merchantid>thestore</merchantid>
  <account>theaccount</account>
  <channel>ECOM</channel>
  <orderid>345</orderid>
  <amount currency="GBP">2000</amount>
  <card>
    <number>4903034000057389</number>
    <expdate>0714</expdate>
    <chname>Mickey Mouse</chname>
    <type>VISA</type>
    <cvn>
      <number>123</number>
      <presind>1</presind>
    </cvn>
  </card>
  <autosettle flag="1" />
  <tssinfo>
    <custnum>567</custnum>
    <prodid>678</prodid>
    <varref>abc</varref>
    <custipaddress>123.4.6.23</custipaddress>
    <address type="billing">
      <code>123|45</code>
      <country>GB</country>
    </address>
  </tssinfo>
  <sha1hash>eeaeaf2751a86edcf0d77e906b2daa08929e7cbe</sha1hash>
</request>""".encode('utf-8'), xml)

        # Test when we have MPI data (in the format returned
        # from GlobalIris3dsVerifySig.proceed_with_auth)
        mpi_data = {'mpi':{'eci': '5',
                           'xid': 'crqAeMwkEL9r4POdxpByWJ1/wYg=',
                           'cavv': 'AAABASY3QHgwUVdEBTdAAAAAAAA=',
                    }}
        data.update(mpi_data)

        xml2 = gateway.build_xml(data)

        self.assertXMLEqual(u"""<?xml version="1.0" encoding="UTF-8" ?>
<request timestamp="20010427124523" type="auth">
  <merchantid>thestore</merchantid>
  <account>theaccount</account>
  <channel>ECOM</channel>
  <orderid>345</orderid>
  <amount currency="GBP">2000</amount>
  <card>
    <number>4903034000057389</number>
    <expdate>0714</expdate>
    <chname>Mickey Mouse</chname>
    <type>VISA</type>
    <cvn>
      <number>123</number>
      <presind>1</presind>
    </cvn>
  </card>
  <autosettle flag="1" />
  <mpi>
    <eci>5</eci>
    <cavv>AAABASY3QHgwUVdEBTdAAAAAAAA=</cavv>
    <xid>crqAeMwkEL9r4POdxpByWJ1/wYg=</xid>
  </mpi>
  <tssinfo>
    <custnum>567</custnum>
    <prodid>678</prodid>
    <varref>abc</varref>
    <custipaddress>123.4.6.23</custipaddress>
    <address type="billing">
      <code>123|45</code>
      <country>GB</country>
    </address>
  </tssinfo>
  <sha1hash>eeaeaf2751a86edcf0d77e906b2daa08929e7cbe</sha1hash>
</request>""".encode('utf-8'), xml2)


    def test_signature(self):
        gateway = self.mk_gateway()
        card = CreditCard(number='5105105105105100',
                          first_name='x',
                          last_name='x',
                          year='1', month='1',
                          verification_value='123')
        gateway.validate_card(card)
        config = gateway.get_config(card)
        sig = gateway.get_standard_signature(
            {
                'timestamp':'20010403123245',
                'amount_normalized':'29900',
                'order_id': 'ORD453-11',
                'currency': 'GBP',
                'card': card,
                }, config)
        self.assertEqual(sig, "9e5b49f4df33b52efa646cce1629bcf8e488f7bb")

    def test_parse_fail_xml(self):
        gateway = self.mk_gateway()
        fail_resp = Dummy200Response('<?xml version="1.0" ?>\r\n<response timestamp="20140212143606">\r\n<result>504</result>\r\n<message>There is no such merchant id.</message>\r\n<orderid>1</orderid>\r\n</response>\r\n')
        retval = gateway.handle_response(fail_resp, "purchase")
        self.assertEqual(retval['status'], 'FAILURE')
        self.assertEqual(retval['message'], 'There is no such merchant id.')
        self.assertEqual(retval['response_code'], "504")
        self.assertEqual(retval['response'], fail_resp)

    def test_parse_success_xml(self):
        gateway = self.mk_gateway()
        success_resp = Dummy200Response('<?xml version="1.0" encoding="UTF-8"?>\r\n\r\n<response timestamp="20140327170816">\r\n  <merchantid>wolfandbadgertest</merchantid>\r\n  <account>internet</account>\r\n  <orderid>2014-03-27_17_08_15_871579556348273697313729</orderid>\r\n  <authcode>12345</authcode>\r\n  <result>00</result>\r\n  <cvnresult>U</cvnresult>\r\n  <avspostcoderesponse>U</avspostcoderesponse>\r\n  <avsaddressresponse>U</avsaddressresponse>\r\n  <batchid>169005</batchid>\r\n  <message>[ test system ] Authorised</message>\r\n  <pasref>13959400966589445</pasref>\r\n  <timetaken>0</timetaken>\r\n  <authtimetaken>0</authtimetaken>\r\n  <cardissuer>\r\n    <bank>AIB BANK</bank>\r\n    <country>IRELAND</country>\r\n    <countrycode>IE</countrycode>\r\n    <region>EUR</region>\r\n  </cardissuer>\r\n  <tss>\r\n    <result>89</result>\r\n    <check id="1001">9</check>\r\n    <check id="1002">9</check>\r\n    <check id="1004">9</check>\r\n    <check id="1005">9</check>\r\n    <check id="1006">9</check>\r\n    <check id="1007">9</check>\r\n    <check id="1008">9</check>\r\n    <check id="1009">9</check>\r\n    <check id="1200">9</check>\r\n    <check id="2001">9</check>\r\n    <check id="2003">0</check>\r\n    <check id="3100">9</check>\r\n    <check id="3101">9</check>\r\n    <check id="3200">9</check>\r\n    <check id="1010">9</check>\r\n    <check id="3202">0</check>\r\n    <check id="1011">9</check>\r\n  </tss>\r\n  <sha1hash>cfb5882353fea0a06919c0f86d9f037b99434026</sha1hash>\r\n</response>\r\n')
        retval = gateway.handle_response(success_resp, "purchase")
        self.assertEqual(retval['status'], 'SUCCESS')
        self.assertEqual(retval['response_code'], '00')
        self.assertEqual(retval['avsaddressresponse'], 'U')
        self.assertEqual(retval['avspostcoderesponse'], 'U')
        self.assertEqual(retval['cvnresult'], 'U')
        self.assertEqual(retval['cardissuer'], {'bank': 'AIB BANK',
                                                'country': 'IRELAND',
                                                'countrycode': 'IE',
                                                'region': 'EUR',
                                                })


    def test_config_for_card_type(self):
        """
        Test that the GateWay object can pick the correct config depending on the card type.
        """
        gateway = GlobalIrisGateway(config={
                'LIVE': dict(SHARED_SECRET="mysecret",
                             MERCHANT_ID="thestore",
                             ACCOUNT="theaccount"),
                'LIVE_AMEX': dict(SHARED_SECRET="mysecret2",
                                  MERCHANT_ID="thestore",
                                  ACCOUNT="theaccountamex"),
                }, test_mode=False)

        vc = self.get_visa_card()
        self.assertTrue(gateway.validate_card(vc)) # needed for side effects

        ac = self.get_amex_card()
        self.assertTrue(gateway.validate_card(ac))

        self.assertEqual("theaccount", gateway.get_config(vc).account)
        self.assertEqual("theaccountamex", gateway.get_config(ac).account)

    def test_purchase_fail(self):
        received_signals = []
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))
        transaction_was_unsuccessful.connect(receive)

        gateway = get_gateway('global_iris')
        card = self.get_visa_card()
        gateway.validate_card(card)
        response = gateway.purchase(Decimal("45.00"), card, options={'order_id': 1})
        # Difficult to test success, because we need dummy card numbers etc.
        # But we can at least test we aren't getting exceptions.
        self.assertEqual(response['status'], 'FAILURE')

        self.assertEqual(received_signals, [transaction_was_unsuccessful])

    def _get_test_cards(self):
        cards = []
        card_dicts = settings.MERCHANT_SETTINGS['global_iris']['TEST_CARDS']
        for card_dict in card_dicts:
            card_type = card_dict['TYPE']
            d = dict(first_name= 'Test',
                     last_name= 'Test',
                     month=1,
                     year=datetime.now().year + 2,
                     number=card_dict['NUMBER'],
                     verification_value="1234" if card_type == "AMEX" else "123")
            card = CreditCard(**d)
            card.expected_response_code = card_dict['RESPONSE_CODE']
            cards.append(card)
        return cards

    @skipIf('TEST' not in settings.MERCHANT_SETTINGS.get('global_iris', {})
            or 'TEST_CARDS' not in settings.MERCHANT_SETTINGS.get('global_iris', {}),
            "gateway not configured")

    def test_purchase_with_test_cards(self):
        # This test requires valid test numbers
        gateway = GlobalIrisGateway()
        if not gateway.test_mode:
            self.fail("MERCHANT_TEST_MODE must be true for running tests")

        for card in self._get_test_cards():
            received_signals = []
            def success(sender, **kwargs):
                received_signals.append(kwargs.get("signal"))
            transaction_was_successful.connect(success)

            def fail(sender, **kwargs):
                received_signals.append(kwargs.get("signal"))
            transaction_was_unsuccessful.connect(fail)

            # Cards with invalid numbers will get caught by billing code, not by
            # the gateway itself.
            try:
                gateway.validate_card(card)
            except CardNotSupported:
                self.assertNotEqual(card.expected_response_code, "00")
                continue # skip the rest


            response = gateway.purchase(Decimal("45.00"), card,
                                        options={'order_id': self.get_order_id(),
                                                 })

            actual_rc = response['response_code']
            expected_rc = card.expected_response_code

            self.assertEqual(actual_rc, expected_rc,
                             "%s != %s - card %s, message: %s" % (actual_rc, expected_rc, card.number, response['message']))
            if card.expected_response_code == "00":
                self.assertEqual(response['status'], 'SUCCESS')
                self.assertEqual(received_signals, [transaction_was_successful])
            else:
                self.assertEqual(response['status'], 'FAILURE')
                self.assertEqual(received_signals, [transaction_was_unsuccessful])

    def test_address_to_code(self):
        gateway = GlobalIrisGateway()
        self.assertEqual(gateway.address_to_code("382, The Road", "WB1 A42"),
                         "142|382")



@skipIf(not settings.MERCHANT_SETTINGS.get("global_iris", None), "integration not configured")
class GlobalIrisRealMpiIntegrationTestCase(BetterXMLCompareMixin, GlobalIrisTestBase, TestCase):

    def test_3ds_verifyenrolled_xml(self):

        expected = """<?xml version="1.0" encoding="UTF-8" ?>
<request timestamp="20100625172305" type="3ds-verifyenrolled">
  <merchantid>thestore</merchantid>
  <account>theaccount</account>
  <orderid>1</orderid>
  <amount currency="GBP">2499</amount>
  <card>
    <number>4903034000057389</number>
    <expdate>0714</expdate>
    <chname>Mickey Mouse</chname>
    <type>VISA</type>
  </card>
  <sha1hash>272d8dde0bf34a0e744f696f2860a7894b687cf7</sha1hash>
</request>
"""
        integration = self.mk_integration()
        gateway = self.mk_gateway()
        card = CreditCard(first_name='Mickey',
                          last_name='Mouse',
                          month=7,
                          year=2014,
                          number='4903034000057389',
                          verification_value='123',
                          )
        gateway.validate_card(card)
        actual_xml = integration.build_3ds_verifyenrolled_xml(
            {'order_id': 1,
             'amount': Decimal('24.99'),
             'card': card,
             'timestamp': datetime(2010,6, 25, 17, 23, 5),
             })
        self.assertXMLEqual(actual_xml, expected)

    def test_parse_3ds_verifyenrolled_response(self):
        example_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<response timestamp="20030625171810">
<merchantid>merchantid</merchantid>
<account>internet</account>
<orderid>orderid</orderid>
<authcode></authcode>
<result>00</result>
<message>Enrolled</message>
<pasref></pasref>
<timetaken>3</timetaken>
<authtimetaken>0</authtimetaken>
<pareq>eJxVUttygkAM/ZUdnitZFlBw4na02tE6bR0vD+0bLlHpFFDASv++u6i1zVNycju54H2dfrIvKsokz3qWY3OLUabyOMm2PWu1fGwF1r3E5a4gGi5IHQuS+ExlGW2JJXHPCjcuVyLYbIRQnrf2o3VMEY+57q05oIsibP+nA4SL02k7mELhKupqxVqF2WVxEgdBpMX6dwE4YJhSsVkKB3RH9ypGFyvNXpkrLW982HcancQzn7MopSkO2RnqmxJZYXQgKjyY1YV39Lt6O5XA4/Fp9xV1b4LcDqdbDcum8xKJ9oqTxFMAMKN5OxotFIXrJNY1otpMH0qYQwP43w08Pn0/W1Ql6+nj+cegonAOKpICs5d3hY+czpdJ+g6HKHBUoNEyk8OwzZaDXXE58R3JtG/as7DBH+IqhZFvpS3zLsBHqeq4VU7/OMTA7Cr45wo/0wNptWlV4Xb8Thftv3A30xs+7GYaokej3c415TxhgIJhUu54TLF2jt33f8ADVyvnA=</pareq>
<url>http://www.acs.com</url>
<enrolled>Y</enrolled>
<xid>7ba3b1e6e6b542489b73243aac050777</xid>
<sha1hash>9eda1f99191d4e994627ddf38550b9f47981f614</sha1hash>
</response>"""
        integration = self.mk_integration()
        retval = integration.handle_3ds_verifyenrolled_response(Dummy200Response(example_xml))
        self.assertEqual(retval.enrolled, True)
        self.assertEqual(retval.response_code, "00")
        self.assertEqual(retval.message, "Enrolled")
        self.assertEqual(retval.url, "http://www.acs.com")
        self.assertEqual(retval.pareq, "eJxVUttygkAM/ZUdnitZFlBw4na02tE6bR0vD+0bLlHpFFDASv++u6i1zVNycju54H2dfrIvKsokz3qWY3OLUabyOMm2PWu1fGwF1r3E5a4gGi5IHQuS+ExlGW2JJXHPCjcuVyLYbIRQnrf2o3VMEY+57q05oIsibP+nA4SL02k7mELhKupqxVqF2WVxEgdBpMX6dwE4YJhSsVkKB3RH9ypGFyvNXpkrLW982HcancQzn7MopSkO2RnqmxJZYXQgKjyY1YV39Lt6O5XA4/Fp9xV1b4LcDqdbDcum8xKJ9oqTxFMAMKN5OxotFIXrJNY1otpMH0qYQwP43w08Pn0/W1Ql6+nj+cegonAOKpICs5d3hY+czpdJ+g6HKHBUoNEyk8OwzZaDXXE58R3JtG/as7DBH+IqhZFvpS3zLsBHqeq4VU7/OMTA7Cr45wo/0wNptWlV4Xb8Thftv3A30xs+7GYaokej3c415TxhgIJhUu54TLF2jt33f8ADVyvnA=")

    def test_parse_3ds_verifyenrolled_response_not_enrolled(self):
        example_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<response timestamp="20030625171810">
<merchantid>merchantid</merchantid>
<account>internet</account>
<orderid>orderid</orderid>
<authcode></authcode>
<result>110</result>
<message>Not Enrolled</message>
<pasref></pasref>
<timetaken>3</timetaken>
<authtimetaken>0</authtimetaken>
<pareq>eJxVUttygkAM/ZUdnitZFlBw4na02tE6bR0vD+0bLlHpFFDASv++u6i1
 zVNycju54H2dfrIvKsokz3qWY3OLUabyOMm2PWu1fGwF1r3E5a4gGi5IH
 QuS+ExlGW2JJXHPCjcuVyLYbIRQnrf2o3VMEY+57q05oIsibP+nA4SL02k
 7mELhKupqxVqF2WVxEgdBpMX6dwE4YJhSsVkKB3RH9ypGFyvNXpkrLW
 982HcancQzn7MopSkO2RnqmxJZYXQgKjyY1YV39Lt6O5XA4/Fp9xV1b4L
 cDqdbDcum8xKJ9oqTxFMAMKN5OxotFIXrJNY1otpMH0qYQwP43w08Pn0
 /W1Ql6+nj+cegonAOKpICs5d3hY+czpdJ+g6HKHBUoNEyk8OwzZaDXXE
 58R3JtG/as7DBH+IqhZFvpS3zLsBHqeq4VU7/OMTA7Cr45wo/0wNptWlV

4Xb8Thftv3A30xs+7GYaokej3c415TxhgIJhUu54TLF2jt33f8ADVyvnA=</pareq>
<url></url>
<enrolled>N</enrolled>
<xid>e9dafe706f7142469c45d4877aaf5984</xid>
<sha1hash>9eda1f99191d4e994627ddf38550b9f47981f614</sha1hash>
</response>
"""
        integration = self.mk_integration()
        retval = integration.handle_3ds_verifyenrolled_response(Dummy200Response(example_xml))
        self.assertEqual(retval.enrolled, False)
        self.assertEqual(retval.response_code, "110")
        self.assertEqual(retval.message, "Not Enrolled")
        self.assertEqual(retval.url, None)
        gateway = self.mk_gateway()
        card = self.get_visa_card()
        gateway.validate_card(card)
        proceed, extra = retval.proceed_with_auth(card)
        self.assertEqual(proceed, True),
        self.assertEqual(extra, {'mpi': {'eci': 6}})

    def test_send_3ds_verifyenrolled(self):
        integration = self.mk_integration()
        gateway = self.mk_gateway()
        card = self.get_visa_card()
        gateway.validate_card(card)
        response = integration.send_3ds_verifyenrolled({
                'order_id': 1,
                'amount': Decimal('24.99'),
                'card': card,
                })

        self.assertEqual(response.error, True)

    def test_encode(self):
        card = self.get_visa_card()
        integration = self.mk_integration()
        gateway = self.mk_gateway()
        gateway.validate_card(card) # Adds 'card_type'
        d = {'some_data': 1,
             'card': card,
             'amount': Decimal('12.34'),
             }
        encoded = integration.encode_merchant_data(d)
        decoded = integration.decode_merchant_data(encoded)
        self.assertEqual(decoded['some_data'], 1)
        self.assertEqual(decoded['card'].number, card.number)
        self.assertEqual(decoded['card'].card_type, Visa)
        self.assertEqual(decoded['amount'], d['amount'])

    def test_3ds_verifysig_xml(self):

        expected = """<?xml version="1.0" encoding="UTF-8" ?>
<request timestamp="20100625172305" type="3ds-verifysig">
  <merchantid>thestore</merchantid>
  <account>theaccount</account>
  <orderid>1</orderid>
  <amount currency="GBP">2499</amount>
  <card>
    <number>4903034000057389</number>
    <expdate>0714</expdate>
    <chname>Mickey Mouse</chname>
    <type>VISA</type>
  </card>
  <pares>xyz</pares>
  <sha1hash>272d8dde0bf34a0e744f696f2860a7894b687cf7</sha1hash>
</request>"""

        integration = self.mk_integration()
        gateway = self.mk_gateway()
        card = CreditCard(first_name='Mickey',
                          last_name='Mouse',
                          month=7,
                          year=2014,
                          number='4903034000057389',
                          verification_value='123',
                          )
        gateway.validate_card(card)
        actual_xml = integration.build_3ds_verifysig_xml('xyz',
                                                         {'order_id': 1,
                                                          'amount': Decimal('24.99'),
                                                          'card': card,
                                                          'timestamp': datetime(2010,6, 25, 17, 23, 5),
                                                          })
        self.assertXMLEqual(actual_xml, expected)

    def test_parse_3ds_verifysig_response_no_auth(self):
        example_xml = """<response timestamp="20100625171823">
<merchantid>merchantid</merchantid>
<account />
<orderid>orderid</orderid>
<result>00</result>
<message>Authentication Successful</message>
<threedsecure>
<status>N</status>
<eci />
<xid />
<cavv />
<algorithm />
</threedsecure>
<sha1hash>e5a7745da5dc32d234c3f52860132c482107e9ac</sha1hash>
</response>
"""
        integration = self.mk_integration()
        gateway = self.mk_gateway()
        card = self.get_visa_card()
        gateway.validate_card(card)
        retval = integration.handle_3ds_verifysig_response(Dummy200Response(example_xml))
        self.assertEqual(retval.response_code, "00")
        self.assertEqual(retval.message, "Authentication Successful")
        self.assertEqual(retval.status, "N")
        self.assertEqual(retval.proceed_with_auth(card)[0], False) # status is "N"

    def test_parse_3ds_verifysig_response_yes_auth(self):
        example_xml = """<response timestamp="20100625171823">
<merchantid>merchantid</merchantid>
<account />
<orderid>orderid</orderid>
<result>00</result>
<message>Authentication Successful</message>
<threedsecure>
<status>Y</status>
<eci>5</eci>
<xid>crqAeMwkEL9r4POdxpByWJ1/wYg=</xid>
<cavv>AAABASY3QHgwUVdEBTdAAAAAAAA=</cavv>
<algorithm />
</threedsecure>
<sha1hash>e5a7745da5dc32d234c3f52860132c482107e9ac</sha1hash>
</response>
"""
        integration = self.mk_integration()
        gateway = self.mk_gateway()
        card = self.get_visa_card()
        gateway.validate_card(card)
        retval = integration.handle_3ds_verifysig_response(Dummy200Response(example_xml))
        self.assertEqual(retval.response_code, "00")
        self.assertEqual(retval.message, "Authentication Successful")
        self.assertEqual(retval.status, "Y")
        proceed, data = retval.proceed_with_auth(card)
        self.assertTrue(proceed)
        self.assertEqual(data, {'mpi':{'eci': '5',
                                       'xid': 'crqAeMwkEL9r4POdxpByWJ1/wYg=',
                                       'cavv': 'AAABASY3QHgwUVdEBTdAAAAAAAA=',
                                       }})

    def test_send_3ds_verifysig(self):
        integration = self.mk_integration()
        gateway = self.mk_gateway()
        card = self.get_visa_card()
        gateway.validate_card(card)
        response = integration.send_3ds_verifysig('xyz', {
                'order_id': 1,
                'amount': Decimal('24.99'),
                'card': card,
                })

        self.assertEqual(response.error, True)
