"""
Template tags for Offsite payment gateways
"""
from django import template
from billing.templatetags.paypal_tags import paypal
from billing.templatetags.world_pay_tags import world_pay
from billing.templatetags.google_checkout_tags import google_checkout
from billing.templatetags.amazon_fps_tags import amazon_fps
from billing.templatetags.braintree_payments_tags import braintree_payments

register = template.Library()

register.tag(google_checkout)
register.tag(paypal)
register.tag(world_pay)
register.tag(amazon_fps)
register.tag(braintree_payments)
