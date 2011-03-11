from django.test import TestCase
from django.utils.html import strip_spaces_between_tags
from billing import get_integration
from django.template import Template, Context
from django.conf import settings

class GoogleCheckoutTestCase(TestCase):
    def setUp(self):
        self.gc = get_integration("google_checkout")
        fields = {"items": [{
                    "name": "name of the item",
                    "description": "Item description",
                    "amount": 1,
                    "id": "999AXZ", 
                    "currency": "USD",
                    "quantity": 1,
                    }],
                  "return_url": "http://127.0.0.1:8000/offsite/google-checkout/",
                  }
        self.gc.add_fields(fields)

    def testFormGen(self):
        tmpl = Template("{% load billing_tags %}{% google_checkout obj %}")
        form = tmpl.render(Context({"obj": self.gc}))
        pregen_form = """<form action="https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/%(mid)s" method="post"><input type="hidden" name="cart" value="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48Y2hlY2tvdXQtc2hvcHBpbmctY2FydCB4bWxucz0iaHR0cDovL2NoZWNrb3V0Lmdvb2dsZS5jb20vc2NoZW1hLzIiPjxzaG9wcGluZy1jYXJ0PjxpdGVtcz48aXRlbT48aXRlbS1uYW1lPm5hbWUgb2YgdGhlIGl0ZW08L2l0ZW0tbmFtZT48aXRlbS1kZXNjcmlwdGlvbj5JdGVtIGRlc2NyaXB0aW9uPC9pdGVtLWRlc2NyaXB0aW9uPjx1bml0LXByaWNlIGN1cnJlbmN5PSJVU0QiPjE8L3VuaXQtcHJpY2U+PHF1YW50aXR5PjE8L3F1YW50aXR5PjxtZXJjaGFudC1pdGVtLWlkPjk5OUFYWjwvbWVyY2hhbnQtaXRlbS1pZD48L2l0ZW0+PC9pdGVtcz48L3Nob3BwaW5nLWNhcnQ+PC9jaGVja291dC1zaG9wcGluZy1jYXJ0Pg==" /><input type="hidden" name="signature" value="3jkvhENlILC3GTVNrXwmvldds4U=" /><input type="image" name="Google Checkout" alt="Fast checkout through Google" src="http://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=%(mid)s&amp;w=180&amp;h=46&amp;style=white&amp;variant=text&amp;loc=en_US" height="46" width="180" /></form>""" %({"mid": settings.GOOGLE_CHECKOUT_MERCHANT_ID})
        self.assertEquals(pregen_form, strip_spaces_between_tags(form).strip())
