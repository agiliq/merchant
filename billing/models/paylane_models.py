# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

from django.db import models


class PaylaneTransaction(models.Model):
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    customer_name = models.CharField(max_length=200)
    customer_email = models.CharField(max_length=200)
    product = models.CharField(max_length=200)
    success = models.BooleanField(default=False)
    error_code = models.IntegerField(default=0)
    error_description = models.CharField(max_length=300, blank=True)
    acquirer_error = models.CharField(max_length=40, blank=True)
    acquirer_description = models.CharField(max_length=300, blank=True)

    def __unicode__(self):
        return u'Transaction for %s (%s)' % (self.customer_name, self.customer_email)

    class Meta:
        app_label = __name__.split(".")[0]


class PaylaneAuthorization(models.Model):
    sale_authorization_id = models.BigIntegerField(db_index=True)
    first_authorization = models.BooleanField(default=False)
    transaction = models.OneToOneField(PaylaneTransaction)

    def __unicode__(self):
        return u'Authorization: %s' % (self.sale_authorization_id)

    class Meta:
        app_label = __name__.split(".")[0]
