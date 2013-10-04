from django.db import models


class GCNewOrderNotification(models.Model):
    notify_type = models.CharField(max_length=255, blank=True)
    serial_number = models.CharField(max_length=255)
    google_order_number = models.CharField(max_length=255)
    buyer_id = models.CharField(max_length=255)

    # Private merchant data
    private_data = models.CharField(max_length=255, blank=True)

    # Buyer Shipping Address details
    shipping_contact_name = models.CharField(max_length=255, blank=True)
    shipping_address1 = models.CharField(max_length=255, blank=True)
    shipping_address2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=255, blank=True)
    shipping_postal_code = models.CharField(max_length=255, blank=True)
    shipping_region = models.CharField(max_length=255, blank=True)
    shipping_country_code = models.CharField(max_length=255, blank=True)
    shipping_email = models.EmailField()
    shipping_company_name = models.CharField(max_length=255, blank=True)
    shipping_fax = models.CharField(max_length=255, blank=True)
    shipping_phone = models.CharField(max_length=255, blank=True)

    # Buyer Billing Address details
    billing_contact_name = models.CharField(max_length=255, blank=True)
    billing_address1 = models.CharField(max_length=255, blank=True)
    billing_address2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=255, blank=True)
    billing_postal_code = models.CharField(max_length=255, blank=True)
    billing_region = models.CharField(max_length=255, blank=True)
    billing_country_code = models.CharField(max_length=255, blank=True)
    billing_email = models.EmailField()
    billing_company_name = models.CharField(max_length=255, blank=True)
    billing_fax = models.CharField(max_length=255, blank=True)
    billing_phone = models.CharField(max_length=255, blank=True)

    # Buyer marketing preferences, bool marketing email allowed
    marketing_email_allowed = models.BooleanField(default=False)

    num_cart_items = models.IntegerField()
    cart_items = models.TextField()

    # Order Adjustment details
    total_tax = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    total_tax_currency = models.CharField(max_length=255, blank=True)
    adjustment_total = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    adjustment_total_currency = models.CharField(max_length=255, blank=True)

    order_total = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    order_total_currency = models.CharField(max_length=255, blank=True)

    financial_order_state = models.CharField(max_length=255, blank=True)
    fulfillment_order_state = models.CharField(max_length=255, blank=True)

    # u'timestamp': [u'2010-10-04T14:05:39.868Z'],
    # timestamp = models.DateTimeField(blank=True, null=True)
    timestamp = models.CharField(max_length=64, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = __name__.split(".")[0]
