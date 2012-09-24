from django.db import models


class WorldPayResponse(models.Model):
    # merchant details
    installation_id = models.CharField(max_length=64)
    company_name = models.CharField(max_length=255, blank=True, null=True)

    # purchase details sent by merchant
    cart_id = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=64)

    # HTML string produced from the amount and currency
    # that were submitted to initiate the payment
    amount_string = models.CharField(max_length=64)
    auth_mode = models.CharField(max_length=64)
    test_mode = models.CharField(max_length=64)

    # transaction details
    transaction_id = models.CharField(max_length=64)
    transaction_status = models.CharField(max_length=64)
    transaction_time = models.CharField(max_length=64)
    auth_amount = models.DecimalField(max_digits=16, decimal_places=2)
    auth_currency = models.CharField(max_length=64)
    auth_amount_string = models.CharField(max_length=64)
    raw_auth_message = models.CharField(max_length=255)
    raw_auth_code = models.CharField(max_length=64)

    # billing address of the user
    name = models.CharField(max_length=255)
    address = models.TextField()
    post_code = models.CharField(max_length=64)
    country_code = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    phone = models.CharField(u'Phone number', max_length=64, blank=True)
    fax = models.CharField(u'Fax number', max_length=64, blank=True)
    email = models.EmailField()

    # future pay id, for recurring payments
    future_pay_id = models.CharField(max_length=64, blank=True)

    card_type = models.CharField(max_length=64, blank=True)
    ip_address = models.IPAddressField(blank=True, null=True)

    class Meta:
        app_label = __name__.split(".")[0]
