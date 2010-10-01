
from django import template

register = template.Library()
from paypal_forms import paypal_buy
from google_checkout_form import google_checkout, google_checkout_form

register.inclusion_tag('billing/paypal.html', takes_context=True)(paypal_buy)
# register.inclusion_tag('billing/google_checkout.html', takes_context=True)(google_checkout)
register.inclusion_tag('billing/google_checkout.html', takes_context=True)(google_checkout_form)
