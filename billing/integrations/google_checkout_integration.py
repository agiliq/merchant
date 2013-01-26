from billing import Integration, IntegrationNotConfigured
from billing.models import GCNewOrderNotification
from django.conf import settings
from xml.dom.minidom import Document
import hmac
import hashlib
import base64
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from billing import signals
from django.conf.urls.defaults import patterns
from django.utils.decorators import method_decorator

SANDBOX_URL = 'https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/%s'
PROD_URL = 'https://checkout.google.com/api/checkout/v2/checkout/Merchant/%s'

BUTTON_SANDBOX_URL = 'http://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=%(merchant_id)s&w=%(width)s&h=%(height)s&style=white&variant=text&loc=en_US'
BUTTON_URL = 'http://checkout.google.com/checkout/buttons/checkout.gif?merchant_id=%(merchant_id)s&w=%(width)s&h=%(height)s&style=white&variant=text&loc=en_US'

csrf_exempt_m = method_decorator(csrf_exempt)
require_POST_m = method_decorator(require_POST)


class GoogleCheckoutIntegration(Integration):
    display_name = 'Google Checkout'

    def __init__(self, options=None):
        if not options:
            options = {}
        super(GoogleCheckoutIntegration, self).__init__(options=options)
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("google_checkout"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                       "configured." % self.display_name)
        google_checkout_settings = merchant_settings["google_checkout"]
        self.merchant_id = google_checkout_settings['MERCHANT_ID']
        self.merchant_key = google_checkout_settings['MERCHANT_KEY']
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

    def _add_nodes(self, doc, parent_node, child_node_name,
                   child_subnode_name, child_node_values):
        """ Helper method that makes it easy to add a bunch of like child nodes
        to a parent node"""
        if child_node_values:
            for value in child_node_values:
                child_node = doc.createElement(unicode(child_node_name))
                child_sub_node = doc.createElement(unicode(child_subnode_name))
                child_node.appendChild(child_sub_node)
                child_sub_node.appendChild(doc.createTextNode(value))
                parent_node.appendChild(child_node)

    def _shipping_allowed_excluded(self, doc, parent_node, data):
        """ Build the nodes for the allowed-areas, excluded-areas
        for shipping-restrictions and address-filters """
        if not data:
            return
        states = data.get('us-state-area', None)
        zips = data.get('us-zip-area', None)
        country = data.get('us-country-area', None)
        world = data.get('world-area', False)
        postal = data.get('postal-area', None)

        self._add_nodes(doc, parent_node, 'us-state-area', 'state', states)
        self._add_nodes(doc, parent_node, 'us-zip-area', 'zip-pattern', zips)

        if country:
            us_country_area = doc.createElement('us-country-area')
            us_country_area.setAttribute('country-area', unicode(country))
            parent_node.appendChild(us_country_area)

        if world:
            parent_node.appendChild(doc.createElement('world-area'))

        if postal:
            for post in postal:
                p_country_code = post.get('country-code', None)
                p_pattern = post.get('postal-code-pattern', None)
                postal_area = doc.createElement('postal-area')
                if p_country_code:
                    c_code = doc.createElement('country-code')
                    c_code.appendChild(doc.createTextNode(unicode(p_country_code)))
                    postal_area.appendChild(c_code)
                if p_pattern:
                    for pp in p_pattern:
                        p_p = doc.createElement('postal-code-pattern')
                        p_p.appendChild(doc.createTextNode(unicode(pp)))
                        postal_area.appendChild(p_p)
                parent_node.appendChild(postal_area)


    def _shipping_restrictions_filters(self, doc, parent_node, data):
        """ process the shipping restriction and address-filter sections for
        the shipping method merchant-calculated-shipping and flat-rate-shipping
        """
        the_allowed_areas = data.get('allowed-areas', None)
        the_excluded_areas = data.get('excluded-areas', None)
        allow_us_po_box = data.get('allow-us-po-box', None)

        if allow_us_po_box is not None:
            allow_po_box = doc.createElement('allow-us-po-box')
            allow_po_box.appendChild(
                    doc.createTextNode(str(allow_us_po_box).lower()))
            parent_node.appendChild(allow_po_box)

        if the_allowed_areas:
            allowed_areas = doc.createElement('allowed-areas')
            parent_node.appendChild(allowed_areas)
            self._shipping_allowed_excluded(doc,
                                            allowed_areas,
                                            the_allowed_areas)

        if the_excluded_areas:
            excluded_areas = doc.createElement('excluded-areas')
            parent_node.appendChild(excluded_areas)
            self._shipping_allowed_excluded(doc,
                                            excluded_areas,
                                            the_excluded_areas)

    def build_xml(self):
        """ Build up the Cart XML. Seperate method for easier unit testing """
        doc = Document()
        root = doc.createElement('checkout-shopping-cart')
        root.setAttribute('xmlns', 'http://checkout.google.com/schema/2')
        doc.appendChild(root)
        cart = doc.createElement('shopping-cart')
        root.appendChild(cart)
        items = doc.createElement('items')
        cart.appendChild(items)

        merchant_private_data = doc.createElement('merchant-private-data')
        cart.appendChild(merchant_private_data)
        private_data = unicode(self.fields.get("private_data", ""))
        merchant_private_data.appendChild(doc.createTextNode(private_data))

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
            if item.get('private-item-data', None):
                it_private = doc.createElement("merchant-private-item-data")
                it.appendChild(it_private)
                it_data = unicode(item.get('private-item-data', ""))
                it_private.appendChild(doc.createTextNode(it_data))

        checkout_flow = doc.createElement('checkout-flow-support')
        root.appendChild(checkout_flow)
        merchant_checkout_flow = doc.createElement('merchant-checkout-flow-support')
        checkout_flow.appendChild(merchant_checkout_flow)
        return_url = doc.createElement('continue-shopping-url')
        return_url.appendChild(doc.createTextNode(self.fields["return_url"]))
        merchant_checkout_flow.appendChild(return_url)

        # supports: flat-rate-shipping, merchant-calculated-shipping, pickup
        # No support for carrier-calculated-shipping yet
        shipping = self.fields.get("shipping-methods", [])
        if shipping:
            shipping_methods = doc.createElement('shipping-methods')
            merchant_checkout_flow.appendChild(shipping_methods)

            for ship_method in shipping:
                # don't put dict.get() because we want these to fail if 
                # they aren't here because they are required.
                shipping_type = doc.createElement(unicode(ship_method["shipping_type"]))
                shipping_type.setAttribute('name', unicode(ship_method["name"]))
                shipping_methods.appendChild(shipping_type)

                shipping_price = doc.createElement('price')
                shipping_price.setAttribute('currency', unicode(ship_method["currency"]))
                shipping_type.appendChild(shipping_price)

                shipping_price_text = doc.createTextNode(unicode(ship_method["price"]))
                shipping_price.appendChild(shipping_price_text)

                restrictions = ship_method.get('shipping-restrictions', None)
                if restrictions:
                    shipping_restrictions = doc.createElement('shipping-restrictions')
                    shipping_type.appendChild(shipping_restrictions)
                    self._shipping_restrictions_filters(doc, 
                                                        shipping_restrictions,
                                                        restrictions)

                address_filters = ship_method.get('address-filters', None)
                if address_filters:
                    address_filters_node = doc.createElement('address-filters')
                    shipping_type.appendChild(address_filters_node)
                    self._shipping_restrictions_filters(doc, 
                                                        address_filters_node,
                                                        address_filters)

        return doc.toxml(encoding="utf-8")

    def generate_cart_xml(self):
        cart_xml = self.build_xml()
        hmac_signature = hmac.new(self.merchant_key, cart_xml, hashlib.sha1).digest()
        self._signature = base64.b64encode(hmac_signature)
        return base64.b64encode(cart_xml)

    def signature(self):
        if not self._signature:
            self.generate_cart_xml()
        return self._signature

    @csrf_exempt_m
    @require_POST_m
    def gc_notify_handler(self, request):
        if request.POST['_type'] == 'new-order-notification':
            self.gc_new_order_notification(request)
        elif request.POST['_type'] == 'order-state-change-notification':
            self.gc_order_state_change_notification(request)
        elif request.POST['_type'] == 'charge-amount-notification':
            # TODO add support for this later
            pass

        return HttpResponse(request.POST['serial-number'])

    def gc_cart_items_blob(self, post_data):
        items = post_data.getlist('shopping-cart.items')
        cart_blob = ''
        for item in items:
            item_id = post_data.get('%s.merchant-item-id' % (item), '')
            item_name = post_data.get('%s.item-name' % (item), '')
            item_desc = post_data.get('%s.item-description' % (item), '')
            item_price = post_data.get('%s.unit-price' % (item), '')
            item_price_currency = post_data.get('%s.unit-price.currency' % (item), '')
            item_quantity = post_data.get('%s.quantity' % (item), '')
            item_private_data = post_data.get('%s.merchant-private-item-data' % (item), '')
            cart_blob += '%(item_id)s\t%(item_name)s\t%(item_desc)s\t%(item_price)s\t%(item_price_currency)s\t%(item_quantity)s\t%(item_private_data)s\n\n' % ({"item_id": item_id,
                                                                                                                                         "item_name": item_name,
                                                                                                                                         "item_desc": item_desc,
                                                                                                                                         "item_price": item_price,
                                                                                                                                         "item_price_currency": item_price_currency,
                                                                                                                                         "item_quantity": item_quantity,
                                                                                                                                         "item_private_data": item_private_data,
                                                                                                                                         })
        return cart_blob

    def gc_new_order_notification(self, request):
        post_data = request.POST.copy()
        data = {}

        resp_fields = {
            "_type": "notify_type",
            "serial-number": "serial_number",
            "google-order-number": "google_order_number",
            "buyer-id": "buyer_id",
            "buyer-shipping-address.contact-name": "shipping_contact_name",
            "buyer-shipping-address.address1": "shipping_address1",
            "buyer-shipping-address.address2": "shipping_address2",
            "buyer-shipping-address.city": "shipping_city",
            "buyer-shipping-address.postal-code": "shipping_postal_code",
            "buyer-shipping-address.region": "shipping_region",
            "buyer-shipping-address.country-code": "shipping_country_code",
            "buyer-shipping-address.email": "shipping_email",
            "buyer-shipping-address.company-name": "shipping_company_name",
            "buyer-shipping-address.fax": "shipping_fax",
            "buyer-shipping-address.phone": "shipping_phone",
            "buyer-billing-address.contact-name": "billing_contact_name",
            "buyer-billing-address.address1": "billing_address1",
            "buyer-billing-address.address2": "billing_address2",
            "buyer-billing-address.city": "billing_city",
            "buyer-billing-address.postal-code": "billing_postal_code",
            "buyer-billing-address.region": "billing_region",
            "buyer-billing-address.country-code": "billing_country_code",
            "buyer-billing-address.email": "billing_email",
            "buyer-billing-address.company-name": "billing_company_name",
            "buyer-billing-address.fax": "billing_fax",
            "buyer-billing-address.phone": "billing_phone",
            "buyer-marketing-preferences.email-allowed": "marketing_email_allowed",
            "order-adjustment.total-tax": "total_tax",
            "order-adjustment.total-tax.currency": "total_tax_currency",
            "order-adjustment.adjustment-total": "adjustment_total",
            "order-adjustment.adjustment-total.currency": "adjustment_total_currency",
            "order-total": "order_total",
            "order-total.currency": "order_total_currency",
            "financial-order-state": "financial_order_state",
            "fulfillment-order-state": "fulfillment_order_state",
            "timestamp": "timestamp",
            "shopping-cart.merchant-private-data": "private_data",
            }

        for (key, val) in resp_fields.iteritems():
            data[val] = post_data.get(key, '')

        data['num_cart_items'] = len(post_data.getlist('shopping-cart.items'))
        data['cart_items'] = self.gc_cart_items_blob(post_data)

        resp = GCNewOrderNotification.objects.create(**data)

    def gc_order_state_change_notification(self, request):
        post_data = request.POST.copy()
        order = GCNewOrderNotification.objects.get(google_order_number=post_data['google-order-number'])
        order.financial_order_state = post_data['new-financial-order-state']
        # Send success signal when order state is charged
        if order.financial_order_state == 'CHARGED':
            signals.transaction_was_successful.send(sender=self.__class__,
                                                    type="purchase",
                                                    response=order)

        order.fulfillment_order_state = post_data['new-fulfillment-order-state']
        order.save()

    def get_urls(self):
        urlpatterns = patterns('',
           (r'^gc-notify-handler/$', self.gc_notify_handler),
                               )
        return urlpatterns
