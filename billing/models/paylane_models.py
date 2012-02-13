# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

from django.db import models

class PaylaneResponse(models.Model):
    #this enables recurring payments
    sale_authorization_id = models.BigIntegerField()

    def __unicode__(self):
        return 'Authorization: %s' % (self.sale_authorization_id)
        
    class Meta:
        app_label = __name__.split(".")[0]
