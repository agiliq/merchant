from django.utils.importlib import import_module
import re
from gateways import *

class GatewayNotConfigured(Exception):
    pass

class BaseGateway(object):
    GATEWAYS = {
        "PAYPAL": {"object": PaypalCardProcess, "transaction_field": "correlationid", "status": "ack"}
        "AUTHORIZE_NET": {"object": AuthorizeNetGateway, "transaction_field": "transaction_id", "status": "response_reason_text"}
        "EWAY": {"object": Eway, "transaction_field": "ewayTrxnNumber", "status": "ewayTrxnStatus"}
        }

    def __init__(self, gateway, *args, **kwargs):
        gateway_filename = "%s_gateway" %gateway
        gateway_modules = import_module("gateways.%s" %gateway_filename)
        gateway_class_name = gateway_filename
        self.gateway_obj = GATEWAYS[gateway]["object"](*args, **kwargs)

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

    def charge(self, amount, credit_card, *args, **kwargs):
        actual_response = self.gateway_obj.purchase(amount, credit_card, *args, **kwargs)
        trnx_id = getattr(actual_response, self.gateway["transaction_field"], None)
        status = getattr(actual_response, self.gateway["status"], None)
        return {"transaction_id": trnx_id, "status": status, "actual": actual_response}
