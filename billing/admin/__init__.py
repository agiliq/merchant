from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from billing.utils.modules import get_models, get_module_names
import billing.models as billing_models

MODELS = getattr(settings, 'MERCHANT_MODELS', None)

for module_name in get_module_names(__name__):
    gateway = module_name.replace('_admin', '')
    if not MODELS or gateway in MODELS:
        __import__('%s.%s' % (__name__, module_name), fromlist="*")

for model in get_models(billing_models):
    if str(model._meta).startswith('billing.'):
        try:
            admin.site.register(model)
        except AlreadyRegistered:
            pass
