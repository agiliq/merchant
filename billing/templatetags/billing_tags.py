"""
Template tags for Offsite payment gateways
"""
from django import template

register = template.Library()
from billing.templatetags.paypal_forms import paypal_buy
from billing.templatetags.google_checkout_form import google_checkout, google_checkout_form
from billing.templatetags.rbs_form import rbs_buy

register.inclusion_tag('billing/paypal.html', takes_context=True)(paypal_buy)
register.inclusion_tag('billing/google_checkout.html', takes_context=True)(google_checkout)
register.inclusion_tag('billing/google_checkout.html', takes_context=True)(google_checkout_form)
register.inclusion_tag('billing/rbs.html', takes_context=True)(rbs_buy)
