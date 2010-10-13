from django.utils.importlib import import_module
from django.conf import settings

class GatewayModuleNotFound(Exception):
    pass

class GatewayNotConfigured(Exception):
    pass

class Gateway(object):
    """Sub-classes to inherit from this and implement the below methods"""

    def purchase(self, money, credit_card, options = {}):
        raise NotImplementedError

    def authorize(self, money, credit_card, options = {}):
        raise NotImplementedError

    def capture(self, money, authorization, options = {}):
        raise NotImplementedError

    def void(self, identification, options = {}):
        raise NotImplementedError

    def credit(self, money, identification, options = {}):
        raise NotImplementedError

    def recurring(self, money, creditcard, options = {}):
        raise NotImplementedError

    def store(self, creditcard, options = {}):
        raise NotImplementedError

    def unstore(self, identification, options = {}):
        raise NotImplementedError

def get_gateway(gateway, *args, **kwargs):
    """Return the gateway instance"""
    gateway_filename = "%s_gateway" %gateway
    gateway_module = None
    for app in settings.INSTALLED_APPS:
        try:
            gateway_module = import_module(".gateways.%s" %gateway_filename, package=app)
        except ImportError:
            pass
    if not gateway_module:
        raise GatewayModuleNotFound("Missing gateway")
    gateway_class_name = "".join(gateway_filename.title().split("_"))
    try:
        return getattr(gateway_module, gateway_class_name)(*args, **kwargs)
    except AttributeError:
        raise GatewayNotConfigured("Missing %s class in the gateway module." %gateway_class_name)
