from django.db import models

# class Card(models.Model):
#     token = models.CharField(primary_key=True, max_length=32)
#     display_number = models.CharField(max_length=20)
#     scheme = models.CharField(max_length=20)
#     address_line1 = models.CharField(max_length=255)
#     address_line2 = models.CharField(max_length=255)
#     address_city = models.CharField(max_length=255)
#     address_postcode = models.CharField(max_length=20)
#     address_state = models.CharField(max_length=255)
#     address_country = models.CharField(max_length=255)
#     created = 

# class Charge(models.Model):
#     token = models.CharField(primary_key=True, max_length=32)
#     card = models.ForeignKey(Card, related_name='charges')
#     success = models.BooleanField()
#     amount = models.DecimalField(max_digits=16, decimal_places=2)
#     currency = models.CharField(max_length=3)
#     description = models.CharField(max_length=255)
#     email = models.EmailField()
#     ip_address = models.IPAddressField()
#     created_at = models.DateTimeField()
#     status_message = models.CharField(max_length=255),
#     error_message = models.CharField(max_length=255),
#     created = 

# class Customer(models.Model):
#     token = models.CharField(primary_key=True, max_length=32)
#     card = models.ForeignKey(Card, related_name='customers')
#     created = 

