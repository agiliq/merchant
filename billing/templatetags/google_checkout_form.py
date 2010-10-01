'''
Template tag for google checkout
'''

import hmac
import hashlib
import base64

from string import split
from xml.dom import minidom
from xml.dom.minidom import Document
from urllib2 import Request, urlopen, HTTPError, URLError

from django.conf import settings

from required import require

MERCHANT_ID = settings.GOOGLE_CHECKOUT_MERCHANT_ID
MERCHANT_KEY = settings.GOOGLE_CHECKOUT_MERCHANT_KEY
CURRENCY = getattr(settings, 'GOOGLE_CHECKOUT_CURRENCY', 'USD')

# URLs for server-to-server request
SANDBOX_URL = 'https://sandbox.google.com/checkout/api/checkout/v2/merchantCheckout/Merchant/' + MERCHANT_ID
URL = 'https://checkout.google.com/api/checkout/v2/merchantCheckout/Merchant/' + MERCHANT_ID

# URLs for browser to server request
F_SANDBOX_URL = 'https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/' + MERCHANT_ID
F_URL = 'https://checkout.google.com/api/checkout/v2/checkout/Merchant/' + MERCHANT_ID
    

BUTTON_SANDBOX_URL = 'http://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=%s&w=180&h=46&style=white&variant=text&loc=en_US' % (MERCHANT_ID)
BUTTON_URL = 'http://checkout.google.com/checkout/buttons/checkout.gif?merchant_id=%s&w=180&h=46&style=white&variant=text&loc=en_US' % (MERCHANT_ID)


def get_checkout_url(context):
    """ makes a request to Google Checkout with an XML cart and parses out 
    the returned checkout URL to which we send the customer when they are 
    ready to check out.
    """
    redirect_url = ''
    req = _create_google_checkout_request(context)
    try:
        response_xml = urlopen(req).read()
    except HTTPError, err:
        raise err
    except URLError, err:
        raise err
    else:
        redirect_url = _parse_google_checkout_response(response_xml)
    return redirect_url

def _create_google_checkout_request(context):
    """constructs a network request containing an XML version of a customer's 
    shopping cart contents to submit to Google Checkout 
    """
    if context['test_mode']:
        url = SANDBOX_URL
    else:
        url = URL
    cart = _build_xml_shopping_cart(context)
    req = Request(url=url, data=cart)
    merchant_id = MERCHANT_ID
    merchant_key = MERCHANT_KEY
    key_id = merchant_id + ':' + merchant_key
    authorization_value = base64.encodestring(key_id)[:-1]
    req.add_header('Authorization', 'Basic %s' % authorization_value)
    req.add_header('Content-Type','application/xml; charset=UTF-8')
    req.add_header('Accept','application/xml; charset=UTF-8')
    return req

def _parse_google_checkout_response(response_xml):
    """ get the XML response from an XML POST to Google Checkout of 
    our shopping cart items """
    redirect_url = ''
    xml_doc = minidom.parseString(response_xml)
    root = xml_doc.documentElement
    node = root.childNodes[1]
    if node.tagName == 'redirect-url':
        redirect_url = node.firstChild.data
    if node.tagName == 'error-message':
        raise RuntimeError(node.firstChild.data)
    return redirect_url
    
    
def _build_xml_shopping_cart(context):
    """ constructs the XML representation of the current customer's
    shopping cart items to POST to the Google Checkout API
    """
    doc = Document()
    root = doc.createElement('checkout-shopping-cart')
    root.setAttribute('xmlns', 'http://checkout.google.com/schema/2')
    doc.appendChild(root)
    shopping_cart = doc.createElement('shopping-cart')
    root.appendChild(shopping_cart)
    items = doc.createElement('items')
    shopping_cart.appendChild(items)
    
    # for cart_item in cart_items:
    item = doc.createElement('item')
    items.appendChild(item)
    
    item_name = doc.createElement('item-name')
    item_name_text = doc.createTextNode(context['item_name'])
    item_name.appendChild(item_name_text)
    item.appendChild(item_name)
    
    item_description = doc.createElement('item-description')
    item_description_text = doc.createTextNode(context['item_name'])
    item_description.appendChild(item_description_text)
    item.appendChild(item_description)
    
    unit_price = doc.createElement('unit-price')
    unit_price.setAttribute('currency', CURRENCY)
    unit_price_text = doc.createTextNode(str(context['amount']))
    unit_price.appendChild(unit_price_text)
    item.appendChild(unit_price)
    
    quantity = doc.createElement('quantity')
    quantity_text = doc.createTextNode(str(context.get('quantity', 1)))
    quantity.appendChild(quantity_text)
    item.appendChild(quantity)
        
    checkout_flow = doc.createElement('checkout-flow-support')
    root.appendChild(checkout_flow)
    merchant_flow = doc.createElement('merchant-checkout-flow-support')
    checkout_flow.appendChild(merchant_flow)
    
    # edit_cart_url_text = context.get('return_url', '')
    # if edit_cart_url_text:
    #     edit_cart_url = doc.createElement('edit-cart-url')
    #     edit_cart_url_text = doc.createTextNode(edit_cart_url_text)
    #     edit_cart_url.appendChild(edit_cart_url_text)
    #     merchant_flow.appendChild(edit_cart_url)
    
    # continue_shopping_url_text = context.get('continue_shopping_url', '')
    continue_shopping_url_text = context.get('return_url', '')
    if continue_shopping_url_text:
        continue_shopping_url = doc.createElement('continue-shopping-url')
        continue_shopping_url_text = doc.createTextNode(continue_shopping_url_text)
        continue_shopping_url.appendChild(continue_shopping_url_text)
        merchant_flow.appendChild(continue_shopping_url)
    
    # shipping_methods = doc.createElement('shipping-methods')
    # merchant_flow.appendChild(shipping_methods)
    
    # flat_rate_shipping = doc.createElement('flat-rate-shipping')
    # flat_rate_shipping.setAttribute('name','FedEx Ground')
    # shipping_methods.appendChild(flat_rate_shipping)
    
    # shipping_price = doc.createElement('price')
    # shipping_price.setAttribute('currency','USD')
    # flat_rate_shipping.appendChild(shipping_price)
    
    # shipping_price_text = doc.createTextNode('9.99')
    # shipping_price.appendChild(shipping_price_text)
    
    # print doc.toprettyxml()
    return doc.toxml(encoding='utf-8')


def get_hmac_signature(cart_xml):
    """returns binary format of checkout xml encrypted with sha1 hash 
    using merchant key as KEY""" 
    return hmac.new(MERCHANT_KEY, cart_xml, hashlib.sha1).digest()


def google_checkout(context):
    '''inclusion tag, fetches the redirect url from google checkout
    to complete the checkout process'''
    require(context, *split('return_url'))
    test_mode = getattr(settings, 'MERCHANT_TEST_MODE', True)
    context['test_mode'] = test_mode
    if test_mode:
        image_url = BUTTON_SANDBOX_URL
    else:
        image_url = BUTTON_URL
    
    dest_url = get_checkout_url(context)
    
    return {'image_url': image_url, 
            'dest_url': dest_url}


def google_checkout_form(context):
    '''inclusion tag to render a form that will be submitted to google
    checkout API'''
    require(context, *split('return_url item_name amount'))
    test_mode = getattr(settings, 'MERCHANT_TEST_MODE', True)
    context['test_mode'] = test_mode
    if test_mode:
        url = F_SANDBOX_URL
        image_url = BUTTON_SANDBOX_URL
    else:
        url = F_URL
        image_url = BUTTON_URL
    
    cart_xml = _build_xml_shopping_cart(context)
    cart = base64.b64encode(cart_xml)
    signature = base64.b64encode(get_hmac_signature(cart_xml))
    
    return {'url': url, 
            'image_url': image_url, 
            'cart': cart,
            'signature': signature,
            'form_submit': True,
            }