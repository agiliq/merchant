"""
Template tags for Offsite payment gateways
"""
from django import template
from billing.templatetags.paypal_tags import paypal
from billing.templatetags.world_pay_tags import world_pay
from billing.templatetags.google_checkout_tags import google_checkout

register = template.Library()

register.tag(google_checkout)
register.tag(paypal)
register.tag(world_pay)
