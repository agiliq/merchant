from django.db import models
from django.conf import settings

User = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class PinCard(models.Model):
    token = models.CharField(max_length=32, db_index=True, editable=False)
    display_number = models.CharField(max_length=20, editable=False)
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    scheme = models.CharField(max_length=20, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    address_city = models.CharField(max_length=255)
    address_postcode = models.CharField(max_length=20)
    address_state = models.CharField(max_length=255)
    address_country = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='pin_cards', blank=True, null=True)

    def __unicode__(self):
        return 'Card %s' % self.display_number

    class Meta:
        app_label = __name__.split(".")[0]


class PinCustomer(models.Model):
    token = models.CharField(unique=True, max_length=32)
    card = models.ForeignKey("billing.PinCard", related_name='customers')
    email = models.EmailField()
    created_at = models.DateTimeField()
    user = models.OneToOneField(User, related_name='pin_customer', blank=True, null=True)

    def __unicode__(self):
        return 'Customer %s' % self.email

    class Meta:
        app_label = __name__.split(".")[0]


class PinCharge(models.Model):
    token = models.CharField(unique=True, max_length=32, editable=False)
    card = models.ForeignKey("billing.PinCard", related_name='charges', editable=False)
    customer = models.ForeignKey("billing.PinCustomer", related_name='customers', null=True, blank=True, editable=False)
    success = models.BooleanField()
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=3)
    description = models.CharField(max_length=255)
    email = models.EmailField()
    ip_address = models.IPAddressField()
    created_at = models.DateTimeField()
    status_message = models.CharField(max_length=255)
    error_message = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name='pin_charges', blank=True, null=True)

    def __unicode__(self):
        return 'Charge %s' % self.email

    class Meta:
        app_label = __name__.split(".")[0]


class PinRefund(models.Model):
    token = models.CharField(unique=True, max_length=32)
    charge = models.ForeignKey("billing.PinCharge", related_name='refunds')
    success = models.BooleanField()
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField()
    status_message = models.CharField(max_length=255)
    error_message = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name='pin_refunds', blank=True, null=True)

    def __unicode__(self):
        return 'Refund %s' % self.charge.email

    class Meta:
        app_label = __name__.split(".")[0]
