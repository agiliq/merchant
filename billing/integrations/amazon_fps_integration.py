from billing.integration import Integration
from django.conf import settings
from boto.fps.connection import FPSConnection

FPS_PROD_API_ENDPOINT = "fps.amazonaws.com"
FPS_SANDBOX_API_ENDPOINT = "fps.sandbox.amazonaws.com"

class AmazonFpsIntegration(Integration):
    # TODO: Document the fields for each flow
    fields = {"transactionAmount": "",
              "pipelineName": "",
              "paymentReason": "",
              "returnURL": "",}

    def __init__(self, options={}):
        self.aws_access_key = options.get("aws_access_key", None) or settings.AWS_ACCESS_KEY
        self.aws_secret_access_key = options.get("aws_secret_access_key", None) or settings.AWS_SECRET_ACCESS_KEY
        super(AmazonFpsIntegration, self).__init__(options=options)
        self.fps_connection = FPSConnection(self.aws_access_key, self.aws_secret_access_key, **options)

    @property
    def service_url(self):
        if self.test_mode:
            return FPS_SANDBOX_API_ENDPOINT
        return FPS_PROD_API_ENDPOINT

    @property
    def link_url(self):
        tmp_fields = self.fields.copy()
        tmp_fields.pop("aws_access_key", None)
        tmp_fields.pop("aws_secret_access_key", None)
        return self.fps_connection.make_url(tmp_fields.pop("returnURL"),
                                            tmp_fields.pop("paymentReason"),
                                            tmp_fields.pop("pipelineName"),
                                            str(tmp_fields.pop("transactionAmount")),
                                            **tmp_fields)

    def purchase(self, amount, options={}):
        tmp_options = options.copy()
        permissible_options = ["senderTokenId", "recipientTokenId", "callerTokenId",
            "chargeFeeTo", "callerReference", "senderReference", "recipientReference",
            "senderDescription", "recipientDescription", "callerDescription",
            "metadata", "transactionDate", "reserve"]
        tmp_options["senderTokenId"] = options["tokenID"]
        for key in options:
            if key not in permissible_options:
                tmp_options.pop(key)
        return self.fps_connection.pay(amount, tmp_options.pop("senderTokenId"), 
                                       callerReference=tmp_options.pop("callerReference"),
                                       **tmp_options)

    def authorize(self, amount, options={}):
        options["reserve"] = True
        return self.purchase(amount, options)

    def capture(self, amount, options={}):
        assert "ReserveTransactionId" in options, "Expecting 'ReserveTransactionId' in options"
        return self.fps_connection.settle(options["ReserveTransactionId"], amount)

    def credit(self, amount, options={}):
        assert "CallerReference" in options, "Expecting 'CallerReference' in options"
        assert "TransactionId" in options, "Expecting 'TransactionId' in options"
        return self.fps_connection.refund(options["CallerReference"],
                                          options["TransactionId"], 
                                          refundAmount=amount,
                                          callerDescription=options.get("description", None))

    def void(self, identification, options={}):
        # Requires the TransactionID to be passed as 'identification'
        return self.fps_connection.cancel(identification, 
                                          options.get("description", None))
