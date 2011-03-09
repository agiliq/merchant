from billing.integration import Integration

RBS_HOSTED_URL_TEST = "https://select-test.wp3.rbsworldpay.com/wcc/purchase"
RBS_HOSTED_URL_LIVE = "https://secure.wp3.rbsworldpay.com/wcc/purchase"

class WorldPayIntegration(Integration):
    # Template for required fields
    fields = {"instId": "",
              "cart_id": "",
              "amount": "",
              "currency": ""}

    def get_urls(self):
        pass

    @property
    def service_url(self):
        if self.test_mode:
            return RBS_HOSTED_URL_TEST
        return RBS_HOSTED_URL_LIVE
