from django.utils.importlib import import_module
from django.conf import settings

class GatewayModuleNotFound(Exception):
    pass

class GatewayNotConfigured(Exception):
    pass

class Gateway(object):
    """Sub-classes to inherit from this and implement the below methods"""

    # To indicate if the gateway is in test mode or not
    test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)

    # The below are optional attributes to be implemented and used by subclases.
    #
    # Set to indicate the default currency for the gateway. Can be a sequence.
    default_currency = ""
    # Sequence of countries supported by the gateway in ISO 3166 alpha-2 format.
    # http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    supported_countries = []
    # Sequence of supported card types by the gateway. Members should be valid 
    # subclasses of the Credit Card object.
    supported_cardtypes = []
    # Home page URL for the gateway. Used for information purposes only.
    homepage_url = ""
    # Name of the gateway.
    display_name = ""
    # Application name or some unique identifier for the gateway.
    application_id = ""

    def purchase(self, money, credit_card, options = {}):
        """One go authorize and capture transaction"""
        raise NotImplementedError

    def authorize(self, money, credit_card, options = {}):
        """Authorization for a future capture transaction"""
        raise NotImplementedError

    def capture(self, money, authorization, options = {}):
        """Capture funds from a previously authorized transaction"""
        raise NotImplementedError

    def void(self, identification, options = {}):
        """Null/Blank/Delete a previous transaction"""
        raise NotImplementedError

    def credit(self, money, identification, options = {}):
        """Refund a previously 'settled' transaction"""
        raise NotImplementedError

    def recurring(self, money, creditcard, options = {}):
        """Setup a recurring transaction"""
        raise NotImplementedError

    def store(self, creditcard, options = {}):
        """Store the credit card and user profile information
        on the gateway for future use"""
        raise NotImplementedError

    def unstore(self, identification, options = {}):
        """Delete the previously stored credit card and user
        profile information on the gateway"""
        raise NotImplementedError

def get_gateway(gateway, *args, **kwargs):
    """Return a gateway instance specified by `gateway` name"""
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
