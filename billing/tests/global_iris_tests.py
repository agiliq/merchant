# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing.tests.utils import BetterXMLCompareMixin
from billing.gateway import get_gateway
from billing.gateways.global_iris_gateway import GlobalIrisGateway
from billing.signals import transaction_was_unsuccessful
from billing.utils.credit_card import Visa


class Dummy200Response(object):
    def __init__(self, content):
        self.status_code = 200
        self.content = content


@skipIf(not settings.MERCHANT_SETTINGS.get("global_iris", None), "gateway not configured")
class GlobalIrisGatewayTestCase(BetterXMLCompareMixin, TestCase):

    def test_request_xml(self):
        gateway = GlobalIrisGateway(merchant_id=12345,
                                    sub_account='mysubaccount',
                                    shared_secret='x',
                                    )
        xml = gateway.build_xml({
                'timestamp': datetime(2001, 4, 27, 12, 45, 23),
                'order_id': '345',
                'amount': Decimal('20.00'),
                'card': Visa(first_name='Mickey',
                             last_name='Mouse',
                             month=7,
                             year=2014,
                             number='4903034000057189',
                             verification_value='123',
                             ),
                'customer_number': 567,
                'billing_address': {
                    'zip_postal_code': 'ABC 123',
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
    <number>4903034000057189</number>
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
  <sha1hash>828a7a3d94127fa23023815712afc473a8724a40</sha1hash>
</request>""".encode('utf-8'), xml)

    def test_signature(self):
        gateway = GlobalIrisGateway(shared_secret="mysecret",
                                    merchant_id="thestore",
                                    sub_account="theaccount")
        sig = gateway.get_signature(
            {
                'timestamp':'20010403123245',
                'amount_normalized':'29900',
                'order_id': 'ORD453-11',
                'currency_code': 'GBP',
                'card': Visa(number='5105105105105100', first_name='x', last_name='x', year='1', month='1',
                             verification_value='123')
                })
        self.assertEqual(sig, "9e5b49f4df33b52efa646cce1629bcf8e488f7bb")

    def test_parse_xml(self):
        gateway = GlobalIrisGateway(shared_secret="mysecret",
                                    merchant_id="thestore",
                                    sub_account="theaccount")
        fail_resp = Dummy200Response('<?xml version="1.0" ?>\r\n<response timestamp="20140212143606">\r\n<result>504</result>\r\n<message>There is no such merchant id.</message>\r\n<orderid>1</orderid>\r\n</response>\r\n')
        retval = gateway.handle_response(fail_resp, "purchase")
        self.assertEqual(retval['status'], 'FAILURE')
        self.assertEqual(retval['message'], 'There is no such merchant id.')
        self.assertEqual(retval['response_code'], 504)
        self.assertEqual(retval['response'], fail_resp)

    def test_purchase(self):
        received_signals = []
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))
        transaction_was_unsuccessful.connect(receive)

        gateway = get_gateway('global_iris')
        card = Visa(first_name='Mickey',
                    last_name='Mouse',
                    month=7,
                    year=2014,
                    number='4903034000057189',
                    verification_value='123',
                    )
        response = gateway.purchase(Decimal("45.00"), card, options={'order_id': 1})
        # Difficult to test success, because we need dummy card numbers etc.
        # But we can at least test we aren't getting exceptions.
        self.assertEqual(response['status'], 'FAILURE')

        self.assertEquals(received_signals, [transaction_was_unsuccessful])


