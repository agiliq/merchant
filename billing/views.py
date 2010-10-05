
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from billing.models import GCNewOrderNotification

def gc_cart_items_blob(post_data):
    items = post_data.getlist('shopping-cart.items')
    cart_blob = ''
    for item in items:
        item_name = post_data.get('%s.item-name' % (item), '')
        item_desc = post_data.get('%s.item-description' % (item), '')
        item_price = post_data.get('%s.unit-price' % (item), '')
        item_price_currency = post_data.get('%s.unit-price.currency' % (item), '')
        item_quantity = post_data.get('%s.quantity' % (item), '')
        cart_blob += '%(item_name)s\t%(item_desc)s\t%(item_price)s\t%(item_price_currency)s\t%(item_quantity)s\n\n' % (locals())
    return cart_blob

def gc_new_order_notification(request):
    post_data = request.POST
    data = {}

    data['notify_type']         = post_data.get('_type', '')
    data['serial_number']       = post_data.get('serial-number', '')
    data['google_order_number'] = post_data.get('google-order-number', '')
    data['buyer_id']            = post_data.get('buyer-id', '')
    
    data['shipping_contact_name'] = post_data.get('buyer-shipping-address.contact-name', '')
    data['shipping_address1']     = post_data.get('buyer-shipping-address.address1', '')
    data['shipping_address2']     = post_data.get('buyer-shipping-address.address2', '')
    data['shipping_city']         = post_data.get('buyer-shipping-address.city', '')
    data['shipping_postal_code']  = post_data.get('buyer-shipping-address.postal-code', '')
    data['shipping_region']       = post_data.get('buyer-shipping-address.region', '')
    data['shipping_country_code'] = post_data.get('buyer-shipping-address.country-code', '')
    data['shipping_email']        = post_data.get('buyer-shipping-address.email', '')
    data['shipping_company_name'] = post_data.get('buyer-shipping-address.company-name', '')
    data['shipping_fax']          = post_data.get('buyer-shipping-address.fax', '')
    data['shipping_phone']        = post_data.get('buyer-shipping-address.phone', '')
    
    data['billing_contact_name'] = post_data.get('buyer-billing-address.contact-name', '')
    data['billing_address1']     = post_data.get('buyer-billing-address.address1', '')
    data['billing_address2']     = post_data.get('buyer-billing-address.address2', '')
    data['billing_city']         = post_data.get('buyer-billing-address.city', '')
    data['billing_postal_code']  = post_data.get('buyer-billing-address.postal-code', '')
    data['billing_region']       = post_data.get('buyer-billing-address.region', '')
    data['billing_country_code'] = post_data.get('buyer-billing-address.country-code', '')
    data['billing_email']        = post_data.get('buyer-billing-address.email', '')
    data['billing_company_name'] = post_data.get('buyer-billing-address.company-name', '')
    data['billing_fax']          = post_data.get('buyer-billing-address.fax', '')
    data['billing_phone']        = post_data.get('buyer-billing-address.phone', '')
    
    data['marketing_email_allowed'] = post_data.get('buyer-marketing-preferences.email-allowed', '') == 'true'
    
    data['num_cart_items'] = len(post_data.getlist('shopping-cart.items'))
    data['cart_items']     = gc_cart_items_blob(post_data)
    
    data['total_tax']                 = post_data.get('order-adjustment.total-tax', '')
    data['total_tax_currency']        = post_data.get('order-adjustment.total-tax.currency', '')
    data['adjustment_total']          = post_data.get('order-adjustment.adjustment-total', '')
    data['adjustment_total_currency'] = post_data.get('order-adjustment.adjustment-total.currency', '')
    
    data['order_total'] = post_data.get('order-total', '')
    data['order_total_currency'] = post_data.get('order-total.currency', '')
    
    data['financial_order_state']   = post_data.get('financial-order-state', '')
    data['fulfillment_order_state'] = post_data.get('fulfillment-order-state', '')
    
    data['timestamp'] = post_data.get('timestamp', '')
    
    GCNewOrderNotification.objects.create(**data)
    

def gc_order_state_change_notification(request):
    post_data = request.POST
    order = GCNewOrderNotification.objects.get(google_order_number=post_data['google-order-number'])
    order.financial_order_state = post_data['new-financial-order-state']
    order.fulfillment_order_state = post_data['new-fulfillment-order-state']
    order.save()
    
@csrf_exempt
@require_POST
def notify_handler(request):
    if request.POST['_type'] == 'new-order-notification':
        gc_new_order_notification(request)
    elif request.POST['_type'] == 'order-state-change-notification':
        gc_order_state_change_notification(request)
    
    return HttpResponse(request.POST['serial-number'])