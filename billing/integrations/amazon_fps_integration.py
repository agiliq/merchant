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
        return self.fps_connection.make_url(tmp_fields.pop("returnURL"),
                                            tmp_fields.pop("paymentReason"),
                                            tmp_fields.pop("pipelineName"),
                                            str(tmp_fields.pop("transactionAmount")),
                                            **tmp_fields)
