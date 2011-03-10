from django.test import TestCase
from django.utils.html import strip_spaces_between_tags
from billing import get_integration
from django.template import Template, Context
from django.conf import settings

class WorldPayTestCase(TestCase):
    def setUp(self):
        self.wp = get_integration("world_pay")
        fields = {
            "cartId": "TEST123",
            "amount": 1,
            "currency": "USD",
            "testMode": 100,
            "futurePayType": "regular",
            "option": 0,
            "noOfPayments": 12,
            "intervalUnit": 3,
            "intervalMult": 1,
            "normalAmount": 1,
            "startDelayUnit": 3,
            "startDelayMult": 1,
            "instId": 12345,
            "signatureFields": "instId:amount:cartId",
            }
        self.wp.add_fields(fields)

    def testFormGen(self):
        # Since the secret key cannot be distributed
        settings.WORLDPAY_MD5_SECRET_KEY = "test"
        tmpl = Template("{% load billing_tags %}{% world_pay obj %}")
        form = tmpl.render(Context({"obj": self.wp}))
        pregen_form = """<form method='post' action='https://select-test.wp3.rbsworldpay.com/wcc/purchase'><input type="hidden" name="futurePayType" value="regular" id="id_futurePayType" /><input type="hidden" name="intervalUnit" value="3" id="id_intervalUnit" /><input type="hidden" name="intervalMult" value="1" id="id_intervalMult" /><input type="hidden" name="option" value="0" id="id_option" /><input type="hidden" name="noOfPayments" value="12" id="id_noOfPayments" /><input type="hidden" name="normalAmount" value="1" id="id_normalAmount" /><input type="hidden" name="startDelayUnit" value="3" id="id_startDelayUnit" /><input type="hidden" name="startDelayMult" value="1" id="id_startDelayMult" /><input type="hidden" name="instId" value="12345" id="id_instId" /><input type="hidden" name="cartId" value="TEST123" id="id_cartId" /><input type="hidden" name="amount" value="1" id="id_amount" /><input type="hidden" name="currency" value="USD" id="id_currency" /><input type="hidden" name="desc" id="id_desc" /><input type="hidden" name="testMode" value="100" id="id_testMode" /><input type="hidden" name="signatureFields" value="instId:amount:cartId" id="id_signatureFields" /><input type="hidden" name="signature" value="75be85df059de95a3407334b7d21273c" id="id_signature" /><input type='submit' value='Pay through WorldPay'/></form>"""
        self.assertEquals(pregen_form, strip_spaces_between_tags(form).strip())

    def testFormGen2(self):
        # Since the secret key cannot be distributed
        self.wp.add_field("signatureFields", "instId:amount:currency:cartId")
        self.wp.fields.pop("signature", None)
        settings.WORLDPAY_MD5_SECRET_KEY = "test"
        tmpl = Template("{% load billing_tags %}{% world_pay obj %}")
        form = tmpl.render(Context({"obj": self.wp}))
        pregen_form = """<form method='post' action='https://select-test.wp3.rbsworldpay.com/wcc/purchase'><input type="hidden" name="futurePayType" value="regular" id="id_futurePayType" /><input type="hidden" name="intervalUnit" value="3" id="id_intervalUnit" /><input type="hidden" name="intervalMult" value="1" id="id_intervalMult" /><input type="hidden" name="option" value="0" id="id_option" /><input type="hidden" name="noOfPayments" value="12" id="id_noOfPayments" /><input type="hidden" name="normalAmount" value="1" id="id_normalAmount" /><input type="hidden" name="startDelayUnit" value="3" id="id_startDelayUnit" /><input type="hidden" name="startDelayMult" value="1" id="id_startDelayMult" /><input type="hidden" name="instId" value="12345" id="id_instId" /><input type="hidden" name="cartId" value="TEST123" id="id_cartId" /><input type="hidden" name="amount" value="1" id="id_amount" /><input type="hidden" name="currency" value="USD" id="id_currency" /><input type="hidden" name="desc" id="id_desc" /><input type="hidden" name="testMode" value="100" id="id_testMode" /><input type="hidden" name="signatureFields" value="instId:amount:currency:cartId" id="id_signatureFields" /><input type="hidden" name="signature" value="9be5c6334f058a294b1ea352634a3dd7" id="id_signature" /><input type='submit' value='Pay through WorldPay'/></form>"""
        self.assertEquals(pregen_form, strip_spaces_between_tags(form).strip())
