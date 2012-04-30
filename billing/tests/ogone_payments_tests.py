from django.test import TestCase
from django.utils.html import strip_spaces_between_tags
from billing import get_integration
from django.template import Template, Context


class OgonePaymentsTestCase(TestCase):
    def setUp(self):
        self.op = get_integration("ogone_payments")
        self.data = {
            'orderID': 21,
            'ownerstate': u'',
            'cn': u'Venkata Ramana',
            'language': 'en_US',
            'ownertown': u'Hyderabad',
            'ownercty': u'IN',
            'exceptionurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'ownerzip': u'Postcode',
            'catalogurl': u'http://127.0.0.1:8000/',
            'currency': u'EUR',
            'amount': u'579',
            'declineurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'homeurl': u'http://127.0.0.1:8000/',
            'cancelurl': u'http://127.0.0.1:8000/offsite/ogone/failure/',
            'accepturl': u'http://127.0.0.1:8000/offsite/ogone/success/',
            'owneraddress': u'Near Madapur PS',
            'com': u'Order #21: Venkata Ramana',
            'email': u'ramana@agiliq.com'
            }

    def testFormGen(self):
        tmpl = Template("{% load ogone_payments from ogone_payments_tags %}{% ogone_payments obj %}")
        form = tmpl.render(Context({"obj": self.op}))
        pregen_form = """<form method="post" action="https://secure.ogone.com/ncol/test/orderstandard.asp"><input type="hidden" name="orderID" value="21" id="id_orderID" /><input type="hidden" name="ownerstate" id="id_ownerstate" /><input type="hidden" name="cn" value="Venkata Ramana" id="id_cn" /><input type="hidden" name="language" value="en_US" id="id_language" /><input type="hidden" name="PSPID" value="ramana" id="id_PSPID" /><input type="hidden" name="ownertown" value="Hyderabad" id="id_ownertown" /><input type="hidden" name="ownercty" value="IN" id="id_ownercty" /><input type="hidden" name="exceptionurl" value="http://127.0.0.1:8000/offsite/ogone/failure/" id="id_exceptionurl" /><input type="hidden" name="catalogurl" value="http://127.0.0.1:8000/" id="id_catalogurl" /><input type="hidden" name="email" value="ramana@agiliq.com" id="id_email" /><input type="hidden" name="currency" value="EUR" id="id_currency" /><input type="hidden" name="ownerzip" value="Postcode" id="id_ownerzip" /><input type="hidden" name="declineurl" value="http://127.0.0.1:8000/offsite/ogone/failure/" id="id_declineurl" /><input type="hidden" name="SHASign" value="B7AE34D419CCFDCDFB1CAE3E6F0D5C3E701FC2CE1C567EFB58636D775155038E002034FC9702FCAE2E0F726BB8BB787DC8E468446ABBFA6A1D19DDA9E40634C6" id="id_SHASign" /><input type="hidden" name="homeurl" value="http://127.0.0.1:8000/" id="id_homeurl" /><input type="hidden" name="cancelurl" value="http://127.0.0.1:8000/offsite/ogone/failure/" id="id_cancelurl" /><input type="hidden" name="amount" value="579" id="id_amount" /><input type="hidden" name="owneraddress" value="Near Madapur PS" id="id_owneraddress" /><input type="hidden" name="com" value="Order #21: Venkata Ramana" id="id_com" /><input type="hidden" name="accepturl" value="http://127.0.0.1:8000/offsite/ogone/success/" id="id_accepturl" /><input type="submit" value="checkout!"></form>"""
        self.assertEquals(pregen_form, strip_spaces_between_tags(form).strip())
