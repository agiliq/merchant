from django.conf import settings
from django.db import models
from billing.utils.modules import get_module_names, get_models

MODELS = getattr(settings, 'MERCHANT_MODELS', None)

# Magic to import all active models
for module_name in get_module_names(__name__):
    gateway = module_name.replace('_models', '')
    if not MODELS or gateway in MODELS:
        module = __import__('%s.%s' % (__name__, module_name), fromlist="*")
        for model in get_models(module):
            globals()[model.__name__] = model
