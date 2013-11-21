from django.db import models

# Response Codes
# APPROVED, DECLINED, ERROR, FRAUD_REVIEW = 1, 2, 3, 4


class AuthorizeAIMResponse(models.Model):
    RESPONSE_CODES = [
        (1, 'Approved'),
        (2, 'Declined'),
        (3, 'Error'),
        (4, 'Held for Review'),
    ]
    ADDRESS_VERIFICATION_RESPONSE = [
        ('A', 'Address(Street) matches,ZIP does not'),
        ('B', 'Address information not provided for AVS check'),
        ('E', 'AVS error'),
        ('G', 'Non-U.S. Card Issuing Bank'),
        ('N', 'No match on Address(Street) or ZIP'),
        ('P', 'AVS not applicable for this transactions'),
        ('R', 'Retry-System unavailable or timed out'),
        ('S', 'Service not supported by issuer'),
        ('U', 'Address information is unavailable'),
        ('W', 'Nine digit Zip matches, Address(Street) does not'),
        ('X', 'Address(Street) and nine digit ZIP match'),
        ('Y', 'Address(Street) and five digit ZIP match'),
        ('Z', 'Five digit Zip matches, Address(Street) does not'),
    ]
    CARD_CODE_RESPONSES = [
        ('', ''),
        ('M', 'Match'),
        ('N', 'No Match'),
        ('P', 'Not Processed'),
        ('S', 'Should have been present'),
        ('U', 'Issuer unable to process request'),
    ]
    response_code = models.IntegerField(choices=RESPONSE_CODES)
    response_reason_code = models.IntegerField(blank=True)
    response_reason_text = models.TextField(blank=True)
    authorization_code = models.CharField(max_length=8)
    address_verification_response = models.CharField(max_length='8', choices=ADDRESS_VERIFICATION_RESPONSE)
    transaction_id = models.CharField(max_length=64)
    invoice_number = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    method = models.CharField(max_length=255, blank=True)
    transaction_type = models.CharField(max_length=255, blank=True)
    customer_id = models.CharField(max_length=64, blank=True)

    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    company = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=64, blank=True)
    state = models.CharField(max_length=64, blank=True)
    zip_code = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    fax = models.CharField(max_length=64, blank=True)
    email = models.EmailField()

    shipping_first_name = models.CharField(max_length=64, blank=True)
    shipping_last_name = models.CharField(max_length=64, blank=True)
    shipping_company = models.CharField(max_length=64, blank=True)
    shipping_address = models.CharField(max_length=64, blank=True)
    shipping_city = models.CharField(max_length=64, blank=True)
    shipping_state = models.CharField(max_length=64, blank=True)
    shipping_zip_code = models.CharField(max_length=64, blank=True)
    shipping_country = models.CharField(max_length=64, blank=True)

    card_code_response = models.CharField(max_length='8', choices=CARD_CODE_RESPONSES, help_text=u'Card Code Verification response')

    class Meta:
        app_label = __name__.split(".")[0]

    def __unicode__(self):
        return "%s, $%s" % (self.get_response_code_display(), self.amount)
