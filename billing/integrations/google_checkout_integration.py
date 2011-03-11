from billing import Integration
from django.conf import settings
from xml.dom.minidom import Document
import hmac, hashlib, base64

SANDBOX_URL = 'https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/%s' 
PROD_URL = 'https://checkout.google.com/api/checkout/v2/checkout/Merchant/%s'

BUTTON_SANDBOX_URL = 'http://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=%(merchant_id)s&w=%(width)s&h=%(height)s&style=white&variant=text&loc=en_US'
BUTTON_URL = 'http://checkout.google.com/checkout/buttons/checkout.gif?merchant_id=%(merchant_id)s&w=%(width)s&h=%(height)s&style=white&variant=text&loc=en_US'

class NotConfiguredError(Exception):
    pass

class GoogleCheckoutIntegration(Integration):
    fields = {}

    def __init__(self, options={}):
        super(GoogleCheckoutIntegration, self).__init__(options=options)
        if not getattr(settings, "GOOGLE_CHECKOUT_MERCHANT_ID", None):
            raise NotConfiguredError("Could not locate the 'GOOGLE_CHECKOUT_MERCHANT_ID' setting")
        self.merchant_id = settings.GOOGLE_CHECKOUT_MERCHANT_ID
        self._signature = None

    @property
    def service_url(self):
        if self.test_mode:
            return SANDBOX_URL % self.merchant_id
        return PROD_URL % self.merchant_id

    def button_image_url(self):
        params = {"merchant_id": self.merchant_id, 
                  "width": self.button_width,
                  "height": self.button_height}
        if self.test_mode:
            return BUTTON_SANDBOX_URL % params
        return BUTTON_URL % params

    @property
    def button_width(self):
        return self.fields.get("button_width", 180)

    @property
    def button_height(self):
        return self.fields.get("button_height", 46)

    def generate_cart_xml(self):
        doc = Document()
        root = doc.createElement('checkout-shopping-cart')
        root.setAttribute('xmlns', 'http://checkout.google.com/schema/2')
        doc.appendChild(root)
        cart = doc.createElement('shopping-cart')
        root.appendChild(cart)
        items = doc.createElement('items')
        cart.appendChild(items)

        ip_items = self.fields.get("items", [])
        for item in ip_items:
            it = doc.createElement("item")
            items.appendChild(it)
            it_name = doc.createElement("item-name")
            it_name.appendChild(doc.createTextNode(unicode(item["name"])))
            it.appendChild(it_name)
            it_descr = doc.createElement('item-description')
            it_descr.appendChild(doc.createTextNode(unicode(item["description"])))
            it.appendChild(it_descr)
            it_price = doc.createElement("unit-price")
            it_price.setAttribute("currency", unicode(item["currency"]))
            it_price.appendChild(doc.createTextNode(unicode(item["amount"])))
            it.appendChild(it_price)
            it_qty = doc.createElement("quantity")
            it_qty.appendChild(doc.createTextNode(unicode(item["quantity"])))
            it.appendChild(it_qty)
            it_unique_id = doc.createElement("merchant-item-id")
            it_unique_id.appendChild(doc.createTextNode(unicode(item["id"])))
            it.appendChild(it_unique_id)

        checkout_flow = doc.createElement('checkout-flow-support')
        root.appendChild(checkout_flow)
        merchant_checkout_flow = doc.createElement('merchant-checkout-flow-support')
        checkout_flow.appendChild(checkout_flow)
        return_url = doc.createElement('continue-shopping-url')
        return_url.appendChild(doc.createTextNode(self.fields["return_url"]))
        merchant_checkout_flow.appendChild(return_url)

        cart_xml = doc.toxml(encoding="utf-8")
        hmac_signature = hmac.new(settings.GOOGLE_CHECKOUT_MERCHANT_KEY, 
                                  cart_xml, 
                                  hashlib.sha1).digest()
        self._signature = base64.b64encode(hmac_signature)
        return base64.b64encode(cart_xml)

    def signature(self):
        if not self._signature:
            self.generate_cart_xml()
        return self._signature
