from django.utils.importlib import import_module
from django.conf import settings

class IntegrationModuleNotFound(Exception):
    pass

class IntegrationNotConfigured(Exception):
    pass

class Integration(object):
    """Base Integration class that needs to be subclassed by
    implementations"""
    # The form fields that will be rendered in the template
    fields = {}
    # The mode of the gateway. Looks into the settings else
    # defaults to True
    test_mode = getattr(settings, "MERCHANT_TEST_MODE", True)

    def __init__(self, options={}):
        if options:
            self.fields.update(options)
    
    def add_field(self, key, value):
        self.fields[key] = value

    def add_fields(self, params):
        for (key, val) in params.iteritems():
            self.add_field(key, val)

def get_integration(integration, *args, **kwargs):
    """Return a integration instance specified by `integration` name"""
    integration_filename = "%s_integration" %integration
    integration_module = None
    for app in settings.INSTALLED_APPS:
        try:
            integration_module = import_module(".integrations.%s" %integration_filename, package=app)
        except ImportError:
            pass
    if not integration_module:
        raise IntegrationModuleNotFound("Missing integration")
    integration_class_name = "".join(integration_filename.title().split("_"))
    try:
        return getattr(integration_module, integration_class_name)(*args, **kwargs)
    except AttributeError:
        raise IntegrationNotConfigured("Missing %s class in the integration module." %integration_class_name)
