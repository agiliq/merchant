# -*- coding: utf-8 -*-
import random
import sys
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing.tests.utils import BetterXMLCompareMixin
from billing.gateway import get_gateway
from billing.gateways.global_iris_gateway import GlobalIrisGateway, CARD_NAMES
from billing.signals import transaction_was_unsuccessful, transaction_was_successful
from billing.utils.credit_card import CreditCard, CardNotSupported


class Dummy200Response(object):
    def __init__(self, content):
        self.status_code = 200
        self.content = content


@skipIf(not settings.MERCHANT_SETTINGS.get("global_iris", None), "gateway not configured")
class GlobalIrisGatewayTestCase(BetterXMLCompareMixin, TestCase):

    def test_request_xml(self):
        gateway = GlobalIrisGateway(
            config={'TEST': dict(MERCHANT_ID=12345,
                                 ACCOUNT='mysubaccount',
                                 SHARED_SECRET='x',
                                 )
                    },
            test_mode=True)
        card = CreditCard(first_name='Mickey',
                          last_name='Mouse',
                          month=7,
                          year=2014,
                          number='4903034000057389',
                          verification_value='123',
                          )
        gateway.validate_card(card)
        xml = gateway.build_xml({
                'timestamp': datetime(2001, 4, 27, 12, 45, 23),
                'order_id': '345',
                'amount': Decimal('20.00'),
                'card': card,
                'customer': '567',
                'billing_address': {
                    'zip': 'ABC 123',
                    'country': 'GB',
                    }
                })

        self.assertXMLEqual(u"""<?xml version="1.0" encoding="UTF-8" ?>
<request timestamp="20010427124523" type="auth">
  <merchantid>12345</merchantid>
  <account>mysubaccount</account>
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
    <address type="billing">
      <code>ABC 123</code>
      <country>GB</country>
    </address>
  </tssinfo>
  <sha1hash>b3676b0a3204a99abdbc055a5651450d8b420808</sha1hash>
</request>""".encode('utf-8'), xml)

    def test_signature(self):
        gateway = GlobalIrisGateway(
            config={'TEST': dict(SHARED_SECRET="mysecret",
                                 MERCHANT_ID="thestore",
                                 ACCOUNT="theaccount")
                    },
            test_mode=True)
        card = CreditCard(number='5105105105105100',
                          first_name='x',
                          last_name='x',
                          year='1', month='1',
                          verification_value='123')
        gateway.validate_card(card)
        config = gateway.get_config(card)
        sig = gateway.get_signature(
            {
                'timestamp':'20010403123245',
                'amount_normalized':'29900',
                'order_id': 'ORD453-11',
                'currency': 'GBP',
                'card': card,
                }, config)
        self.assertEqual(sig, "9e5b49f4df33b52efa646cce1629bcf8e488f7bb")

    def test_parse_xml(self):
        gateway = GlobalIrisGateway(config={'TEST': dict(SHARED_SECRET="mysecret",
                                                         MERCHANT_ID="thestore",
                                                         ACCOUNT="theaccount")
                                            },
                                    test_mode=True)
        fail_resp = Dummy200Response('<?xml version="1.0" ?>\r\n<response timestamp="20140212143606">\r\n<result>504</result>\r\n<message>There is no such merchant id.</message>\r\n<orderid>1</orderid>\r\n</response>\r\n')
        retval = gateway.handle_response(fail_resp, "purchase")
        self.assertEqual(retval['status'], 'FAILURE')
        self.assertEqual(retval['message'], 'There is no such merchant id.')
        self.assertEqual(retval['response_code'], "504")
        self.assertEqual(retval['response'], fail_resp)

    def _visa_card(self):
        return CreditCard(first_name='Mickey',
                          last_name='Mouse',
                          month=7,
                          year=2035,
                          number='4903034000057389',
                          verification_value='123',
                          )

    def _amex_card(self):
        return CreditCard(first_name='Donald',
                          last_name='Duck',
                          month=8,
                          year=2035,
                          number='374101012180018',
                          verification_value='4567',
                          )

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

        vc = self._visa_card()
        self.assertTrue(gateway.validate_card(vc)) # needed for side effects

        ac = self._amex_card()
        self.assertTrue(gateway.validate_card(ac))

        self.assertEqual("theaccount", gateway.get_config(vc).account)
        self.assertEqual("theaccountamex", gateway.get_config(ac).account)

    def test_purchase_fail(self):
        received_signals = []
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))
        transaction_was_unsuccessful.connect(receive)

        gateway = get_gateway('global_iris')
        card = self._visa_card()
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

    @skipIf('TEST' not in settings.MERCHANT_SETTINGS['global_iris']
            or 'TEST_CARDS' not in settings.MERCHANT_SETTINGS['global_iris'],
            "gateway not configured")

    def _get_order_id(self):
        # Need unique IDs for orders
        return str(datetime.now()).replace(':', '_').replace(' ', '_').replace('.', '_') + str(random.randint(0, sys.maxint))

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
                                        options={'order_id': self._get_order_id(),
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
