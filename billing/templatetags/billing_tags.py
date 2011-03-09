"""
Template tags for Offsite payment gateways
"""
from django import template

register = template.Library()
from billing.templatetags.paypal_forms import paypal
from billing.templatetags.google_checkout_form import google_checkout, google_checkout_form
from billing.templatetags.world_pay_tags import world_pay

register.inclusion_tag('billing/google_checkout.html', takes_context=True)(google_checkout)
register.inclusion_tag('billing/google_checkout.html', takes_context=True)(google_checkout_form)
register.tag(paypal)
register.tag(world_pay)
