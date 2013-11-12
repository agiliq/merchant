"""
Braintree Payments Transparent Redirect Tests.
"""
from django.conf import settings
from django.test import TestCase
from django.utils.unittest.case import skipIf

from billing import get_integration


@skipIf(not settings.MERCHANT_SETTINGS.get("braintree_payments", None), "gateway not configured")
class BraintreePaymentsIntegrationTestCase(TestCase):
    urls = "billing.tests.test_urls"

    def setUp(self):
        self.bp = get_integration("braintree_payments")
        fields = {
            "transaction": {
                "type": "sale",
                "amount": "10.00",
                "order_id": 1,
                "customer": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    },
                }
            }
        self.bp.add_fields(fields)

    def testFormFields(self):
        self.assertEquals(self.bp.fields, {"transaction__type": "sale",
                                           "transaction__amount": "10.00",
                                           "transaction__order_id": 1,
                                           "transaction__customer__first_name": "John",
                                           "transaction__customer__last_name": "Doe",
                                           "transaction__customer__email": "john.doe@example.com"})

    # Need to think about the tests below because they are dynamic because
    # of the hashes and the timestamps.
    # def testFormGen(self):
    #     tmpl = Template("{% load braintree_payments from braintree_payments_tags %}{% braintree_payments obj %}")
    #     form = tmpl.render(Context({"obj": self.bp}))
    #     print self.bp.generate_form()
    #     pregen_form = """""" %(settings.BRAINTREE_MERCHANT_ACCOUNT_ID)
    #     self.assertEquals(pregen_form, strip_spaces_between_tags(form).strip())

    # def testFormGen2(self):
    #     tmpl = Template("{% load braintree_payments from braintree_payments_tags %}{% braintree_payments obj %}")
    #     form = tmpl.render(Context({"obj": self.bp}))
    #     pregen_form = u"""%s""" %(settings.BRAINTREE_MERCHANT_ACCOUNT_ID)
    #     self.assertEquals(pregen_form, strip_spaces_between_tags(form).strip())
