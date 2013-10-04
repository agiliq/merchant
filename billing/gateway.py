from django.utils.importlib import import_module
from django.conf import settings
from .utils.credit_card import CardNotSupported

gateway_cache = {}


class GatewayModuleNotFound(Exception):
    pass


class GatewayNotConfigured(Exception):
    pass


class InvalidData(Exception):
    pass


class Gateway(object):
    """Sub-classes to inherit from this and implement the below methods"""

    # To indicate if the gateway is in test mode or not
    test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)

    # The below are optional attributes to be implemented and used by subclases.
    #
    # Set to indicate the default currency for the gateway.
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

    def validate_card(self, credit_card):
        """Checks if the credit card is supported by the gateway
        and calls the `is_valid` method on it. Responsibility
        of the gateway author to use this method before every
        card transaction."""
        card_supported = None
        for card in self.supported_cardtypes:
            card_supported = card.regexp.match(credit_card.number)
            if card_supported:
                credit_card.card_type = card
                break
        if not card_supported:
            raise CardNotSupported("This credit card is not "
                                   "supported by the gateway.")
        # Gateways might provide some random number which
        # might not pass Luhn's test.
        if self.test_mode:
            return True
        return credit_card.is_valid()

    def purchase(self, money, credit_card, options=None):
        """One go authorize and capture transaction"""
        raise NotImplementedError

    def authorize(self, money, credit_card, options=None):
        """Authorization for a future capture transaction"""
        raise NotImplementedError

    def capture(self, money, authorization, options=None):
        """Capture funds from a previously authorized transaction"""
        raise NotImplementedError

    def void(self, identification, options=None):
        """Null/Blank/Delete a previous transaction"""
        raise NotImplementedError

    def credit(self, money, identification, options=None):
        """Refund a previously 'settled' transaction"""
        raise NotImplementedError

    def recurring(self, money, creditcard, options=None):
        """Setup a recurring transaction"""
        raise NotImplementedError

    def store(self, creditcard, options=None):
        """Store the credit card and user profile information
        on the gateway for future use"""
        raise NotImplementedError

    def unstore(self, identification, options=None):
        """Delete the previously stored credit card and user
        profile information on the gateway"""
        raise NotImplementedError


def get_gateway(gateway, *args, **kwargs):
    """
    Return a gateway instance specified by `gateway` name.
    This caches gateway classes in a module-level dictionnary to avoid hitting
    the filesystem every time we require a gateway.

    Should the list of available gateways change at runtime, one should then
    invalidate the cache, the simplest of ways would be to:

    >>> gateway_cache = {}
    """
    # Is the class in the cache?
    clazz = gateway_cache.get(gateway, None)
    if not clazz:
        # Let's actually load it (it's not in the cache)
        gateway_filename = "%s_gateway" % gateway
        gateway_module = None
        for app in settings.INSTALLED_APPS:
            try:
                gateway_module = import_module(".gateways.%s" % gateway_filename, package=app)
            except ImportError:
                pass
        if not gateway_module:
            raise GatewayModuleNotFound("Missing gateway: %s" % (gateway))
        gateway_class_name = "".join(gateway_filename.title().split("_"))
        try:
            clazz = getattr(gateway_module, gateway_class_name)
        except AttributeError:
            raise GatewayNotConfigured("Missing %s class in the gateway module." % gateway_class_name)
        gateway_cache[gateway] = clazz
    # We either hit the cache or load our class object, let's return an instance
    # of it.
    return clazz(*args, **kwargs)
