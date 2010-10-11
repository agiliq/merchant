from gateways import *

class GatewayNotConfigured(Exception):
    pass

class Merchant(object):
    GATEWAYS = {
        "PAYPAL": {"object": PaypalCardProcess, "transaction_field": "correlationid", "status": "ack"}
        "AUTHORIZE_NET": {"object": AuthorizeNetGateway, "transaction_field": "transaction_id", "status": "response_reason_text"}
        "EWAY": {"object": Eway, "transaction_field": "ewayTrxnNumber", "status": "ewayTrxnStatus"}
        }

    def __init__(self, gateway, *args, **kwargs):
        if gateway not in self.GATEWAYS:
            raise GatewayNotConfigured("Missing gateway.")
        self.gateway = GATEWAYS[gateway]
        self.gateway_obj = GATEWAYS[gateway]["object"](*args, **kwargs)

    def charge(self, amount, credit_card, *args, **kwargs):
        actual_response = self.gateway_obj.purchase(amount, credit_card, *args, **kwargs)
        trnx_id = getattr(actual_response, self.gateway["transaction_field"], None)
        status = getattr(actual_response, self.gateway["status"], None)
        return {"transaction_id": trnx_id, "status": status, "actual": actual_response}
