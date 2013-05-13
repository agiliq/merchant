from billing import Integration, IntegrationNotConfigured
from billing.models import GCNewOrderNotification
from django.conf import settings
from xml.dom import minidom
import hmac
import hashlib
import base64
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, QueryDict
from billing import signals
from django.conf.urls import patterns
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

SANDBOX_URL = 'https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/%s'
PROD_URL = 'https://checkout.google.com/api/checkout/v2/checkout/Merchant/%s'

BUTTON_SANDBOX_URL = 'https://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=%(merchant_id)s&w=%(width)s&h=%(height)s&style=white&variant=text&loc=en_US'
BUTTON_URL = 'https://checkout.google.com/buttons/checkout.gif?merchant_id=%(merchant_id)s&w=%(width)s&h=%(height)s&style=white&variant=text&loc=en_US'

csrf_exempt_m = method_decorator(csrf_exempt)
require_POST_m = method_decorator(require_POST)


class GoogleCheckoutIntegration(Integration):
    display_name = 'Google Checkout'
    template = "billing/google_checkout.html"

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


    def _process_tax_rule(self, doc, parent_node, node_name, data, show_shipping_tax=True):
        """ process a tax rule default_tax_rule, and alternative_tax_rule"""
        tax_rule = doc.createElement(node_name)
        parent_node.appendChild(tax_rule)
        shipping_taxed = data.get('shipping-taxed', False)
        rate = data.get('rate', 0)
        tax_area = data.get('tax-area', {})
        zips = tax_area.get('us-zip-area', [])
        states = tax_area.get('us-state-area', [])
        postal = tax_area.get('postal-area', [])
        country = tax_area.get('us-country-area', None)
        word_area = tax_area.get('world-area', False)

        if shipping_taxed is not None and show_shipping_tax:
            shippingtaxed_node = doc.createElement('shipping-taxed')
            shippingtaxed_node.appendChild(
            doc.createTextNode(str(shipping_taxed).lower()))
            tax_rule.appendChild(shippingtaxed_node)

        rate_node = doc.createElement('rate')
        rate_node.appendChild(
        doc.createTextNode(str(rate)))
        tax_rule.appendChild(rate_node)

        # if there is more then one area then the tag switches from
        # tax-area to tax-areas.
        total_areas = len(zips) + len(states) + len(postal)
        if word_area:
            total_areas += 1
        if country is not None:
            total_areas += 1

        if total_areas == 1:
            tax_area_label = 'tax-area'
        else:
            tax_area_label = 'tax-areas'

        tax_area_node = doc.createElement(tax_area_label)
        tax_rule.appendChild(tax_area_node)

        self._add_nodes(doc, tax_area_node, 'us-state-area', 'state', states)
        self._add_nodes(doc, tax_area_node, 'us-zip-area', 'zip-pattern', zips)

        if country is not None:
            us_country_area = doc.createElement('us-country-area')
            us_country_area.setAttribute('country-area', unicode(country))
            tax_area_node.appendChild(us_country_area)

        if word_area:
            tax_area_node.appendChild(doc.createElement('world-area'))

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
                tax_area_node.appendChild(postal_area)

    def _alt_tax_tables(self, doc, parent_node, data):
        """ Alternative Tax tables """
        alt_tax_tables = data.get('alternate-tax-tables', None)
        if not alt_tax_tables:
            return

        alt_tax_tables_node = doc.createElement('alternate-tax-tables')
        parent_node.appendChild(alt_tax_tables_node)

        for alt_tax_table in alt_tax_tables:
            alt_tax_table_node = doc.createElement('alternate-tax-table')
            alt_tax_table_node.setAttribute('name', unicode(alt_tax_table.get('name')))
            alt_tax_table_node.setAttribute('standalone', unicode(str(alt_tax_table.get('standalone', False)).lower()))
            alt_tax_tables_node.appendChild(alt_tax_table_node)

            # if there are no rules we still want to show the element <alternate-tax-rules/>
            alt_tax_rules = alt_tax_table.get('alternative-tax-rules', [])
            alt_tax_rules_node = doc.createElement('alternate-tax-rules')
            alt_tax_table_node.appendChild(alt_tax_rules_node)

            for tax_rule in alt_tax_rules:
                self._process_tax_rule(doc, alt_tax_rules_node, 'alternate-tax-rule', tax_rule, show_shipping_tax=False)

    def _default_tax_table(self, doc, parent_node, data):
        """ process default tax table """
        default_tax_table_node = doc.createElement('default-tax-table')
        parent_node.appendChild(default_tax_table_node)

        tax_rules_node = doc.createElement('tax-rules')
        default_tax_table_node.appendChild(tax_rules_node)

        default_tax_table = data.get('default-tax-table', None)
        if default_tax_table:
            tax_rules = default_tax_table.get('tax-rules', [])
            for tax_rule in tax_rules:
                self._process_tax_rule(doc, tax_rules_node, 'default-tax-rule', tax_rule)

    def _taxes(self, doc, parent_node, data):
        """ Process the taxes section """

        tax_tables = doc.createElement('tax-tables')
        parent_node.appendChild(tax_tables)

        self._default_tax_table(doc, tax_tables, data)
        self._alt_tax_tables(doc, tax_tables, data)

    def _process_item(self, doc, parent, item, item_tag_name="item"):
        it = doc.createElement(item_tag_name)
        parent.appendChild(it)
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
        if 'private-item-data' in item:
            it_private = doc.createElement("merchant-private-item-data")
            it.appendChild(it_private)
            it_data = unicode(item.get('private-item-data', ""))
            it_private.appendChild(doc.createTextNode(it_data))
        if 'subscription' in item:
            subscription = item['subscription']
            it_subscription = doc.createElement("subscription")
            if "type" in subscription:
                it_subscription.setAttribute('type', unicode(subscription["type"]))
            if "period" in subscription:
                it_subscription.setAttribute('period', unicode(subscription["period"]))
            if "start-date" in subscription:
                it_subscription.setAttribute('start-date', unicode(subscription["start-date"]))
            if "no-charge-after" in subscription:
                it_subscription.setAttribute('no-charge-after', unicode(subscription["no-charge-after"]))
            it.appendChild(it_subscription)
            if "payments" in subscription:
                it_payments = doc.createElement("payments")
                it_subscription.appendChild(it_payments)
                payment_items = subscription["payments"]
                for payment in payment_items:
                    it_subscription_payment = doc.createElement("subscription-payment")
                    it_payments.appendChild(it_subscription_payment)
                    if 'times' in payment:
                        it_subscription_payment.setAttribute('times', unicode(payment["times"]))
                    maximum_charge = doc.createElement("maximum-charge")
                    maximum_charge.setAttribute("currency", unicode(payment["currency"]))
                    it_subscription_payment.appendChild(maximum_charge)
                    maximum_charge.appendChild(doc.createTextNode(unicode(payment["maximum-charge"])))
            if "recurrent-items" in subscription:
                recurrent_items = subscription["recurrent-items"]
                for recurrent_item in recurrent_items:
                    self._process_item(doc, it_subscription, recurrent_item, item_tag_name="recurrent-item")

        if "digital-content" in item:
            digital_content = item['digital-content']
            it_dc = doc.createElement("digital-content")
            it.appendChild(it_dc)
            if "display-disposition" in digital_content:
                dc_dd = doc.createElement('display-disposition')
                dc_dd.appendChild(doc.createTextNode(unicode(digital_content["display-disposition"])))
                it_dc.appendChild(dc_dd)
            if "description" in digital_content:
                dc_descr = doc.createElement('description')
                dc_descr.appendChild(doc.createTextNode(unicode(digital_content["description"])))
                it_dc.appendChild(dc_descr)
            if "email-delivery" in digital_content:
                dc_email = doc.createElement('email-delivery')
                dc_email.appendChild(doc.createTextNode(unicode(digital_content["email-delivery"])))
                it_dc.appendChild(dc_email)
            if "key" in digital_content:
                dc_key = doc.createElement('key')
                dc_key.appendChild(doc.createTextNode(unicode(digital_content["key"])))
                it_dc.appendChild(dc_key)
            if "url" in digital_content:
                dc_url = doc.createElement('url')
                dc_url.appendChild(doc.createTextNode(unicode(digital_content["url"])))
                it_dc.appendChild(dc_url)

        if 'tax-table-selector' in item:
            tax_table_selector_node = doc.createElement('tax-table-selector')
            it.appendChild(tax_table_selector_node)
            it_tax_table = unicode(item.get('tax-table-selector', ""))
            tax_table_selector_node.appendChild(doc.createTextNode(it_tax_table))

    def build_xml(self):
        """ Build up the Cart XML. Seperate method for easier unit testing """
        doc = minidom.Document()
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
            self._process_item(doc, items, item)

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

        # add support for taxes.
        # both default-tax-table and alternate-tax-tables is supported.
        taxes = self.fields.get("tax-tables", None)
        if taxes:
            self._taxes(doc, merchant_checkout_flow, taxes)

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
        #get the Authorization string from the Google POST header
        auth_string = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_string:
            #decode the Authorization string and remove Basic portion
            plain_string = base64.b64decode(auth_string.lstrip('Basic '))
            #split the decoded string at the ':'
            split_string = plain_string.split(':')
            merchant_id = split_string[0]
            merchant_key = split_string[1]
            if self.check_auth(merchant_id, merchant_key):
                data = self.parse_response(request.body)

                type = data.get('type', "")
                serial_number = data.get('serial-number', "").strip()

                if type == 'new-order-notification':
                    self.gc_new_order_notification(data)
                elif type == 'order-state-change-notification':
                    self.gc_order_state_change_notification(data)
                elif type == 'charge-amount-notification':
                    self.gc_charge_amount_notification(data)

                # Create Response
                doc = minidom.Document()
                notification_acknowledgment = doc.createElement("notification-acknowledgment")
                notification_acknowledgment.setAttribute("xmlns","http://checkout.google.com/schema/2")
                notification_acknowledgment.setAttribute("serial-number", serial_number)
                doc.appendChild(notification_acknowledgment)
                ack = doc.toxml(encoding="utf-8")

                return HttpResponse(content=ack, content_type="text/xml; charset=UTF-8")
            else:
                raise PermissionDenied
        else:
            raise PermissionDenied

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

    def gc_new_order_notification(self, post_data):
        data = {}

        resp_fields = {
            "type": "notify_type",
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

    def gc_order_state_change_notification(self, post_data):
        order = GCNewOrderNotification.objects.get(google_order_number=post_data['google-order-number'])
        order.financial_order_state = post_data['new-financial-order-state']
        order.fulfillment_order_state = post_data['new-fulfillment-order-state']
        order.save()

    def gc_charge_amount_notification(self, post_data):
        order = GCNewOrderNotification.objects.get(google_order_number=post_data['google-order-number'])
        post_data['local_order'] = order
        signals.transaction_was_successful.send(sender=self.__class__,
                                                    type="purchase",
                                                    response=post_data)

    def get_urls(self):
        urlpatterns = patterns('',
           (r'^gc-notify-handler/$', self.gc_notify_handler),
                               )
        return urlpatterns

    def check_auth(self, merchant_id, merchant_key):
        "Check to ensure valid Google notification."
        if merchant_id == self.merchant_id and merchant_key == self.merchant_key:
            return True
        else: return False

    def parse_response(self, response):
        dom = minidom.parseString(response)
        response_type = dom.childNodes[0].localName #get the reaponse type
        #use this dictionary to determine which items will be taken from the reaponse
        result = QueryDict("", mutable=True)
        result['type'] = response_type
        # load root values
        result.update(self.load_child_nodes(dom.childNodes[0], is_root=True, ignore_nodes=["items"]))
        # load items
        items_arr = []
        items_node = dom.getElementsByTagName('items')
        if items_node:
            n = 0
            for item in items_node[0].childNodes:
                if item.localName:
                    # load root item values
                    item_name = 'item-%s' % n
                    for key, value in self.load_child_nodes(item, is_root=True, ignore_nodes=['subscription', 'digital-content']).items():
                        result['%s.%s' % (item_name, key)] = value
                    n += 1
                    items_arr.append(item_name)
            result.setlist('shopping-cart.items', items_arr)

        return result

    def load_child_nodes(self, node, load_attributes=True, load_complex_nodes=True, is_root=False, ignore_nodes=[]):
        result={}
        if node:
            if is_root:
                for key, value in node.attributes.items():
                    result[str(key)] = value
            for n in node.childNodes:
                if n.localName and n.localName not in ignore_nodes:
                    if load_attributes:
                        for key, value in n.attributes.items():
                            if is_root:
                                result['%s.%s' % (str(n.localName), str(key))] = value
                            else:
                                result['%s.%s.%s' % (str(node.localName), str(n.localName), str(key))] = value
                    if len(n.childNodes) > 1 and load_complex_nodes:
                        for key, value in self.load_child_nodes(n, ignore_nodes=ignore_nodes).items():
                            if is_root:
                                result[key] = value
                            else:
                                result['%s.%s' % (str(node.localName), str(key))] = value
                    elif n.firstChild:
                        if is_root:
                            result[str(n.localName)] = n.firstChild.data
                        else:
                            result['%s.%s' % (str(node.localName), str(n.localName))] = n.firstChild.data
                    else:
                        if is_root:
                            result[str(n.localName)] = ""
                        else:
                            result['%s.%s' % (str(node.localName), str(n.localName))] = ""
        return result
