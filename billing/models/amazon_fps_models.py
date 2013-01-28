from django.db import models


class AmazonFPSResponse(models.Model):
    """ See This doc for a list of fields available, and what they mean.
    http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/AWSFPSIPNDetails.html """
    buyerEmail = models.EmailField()
    buyerName = models.CharField(max_length=75)
    callerReference = models.CharField(max_length=100)
    notificationType = models.CharField(max_length=50)
    operation = models.CharField(max_length=20)
    paymentMethod = models.CharField(max_length=5)
    recipientEmail = models.EmailField()
    recipientName = models.CharField(max_length=75)
    statusCode = models.CharField(max_length=50)
    statusMessage = models.TextField()
    # Because currency is sent along
    transactionAmount = models.CharField(max_length=20)
    transactionDate = models.DateTimeField()
    transactionId = models.CharField(max_length=50, db_index=True)
    transactionStatus = models.CharField(max_length=50)

    customerEmail = models.EmailField(blank=True, null=True)
    customerName = models.CharField(max_length=75, blank=True, null=True)
    # Address fields
    addressFullName = models.CharField(max_length=100, blank=True, null=True)
    addressLine1 = models.CharField(max_length=100, blank=True, null=True)
    addressLine2 = models.CharField(max_length=100, blank=True, null=True)
    addressState = models.CharField(max_length=50, blank=True, null=True)
    addressZip = models.CharField(max_length=25, blank=True, null=True)
    addressCountry = models.CharField(max_length=25, blank=True, null=True)
    addressPhone = models.CharField(max_length=25, blank=True, null=True)

    def __unicode__(self):
        return "%s : %s" % (self.transactionId, self.statusCode)

    class Meta:
        app_label = __name__.split(".")[0]
