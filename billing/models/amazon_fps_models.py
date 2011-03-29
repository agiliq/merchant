from django.db import models

class AmazonFPSResponse(models.Model):
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

    def __unicode__(self):
        return "%s : %s" %(self.transactionId, self.statusCode)

    class Meta:
        app_label = __name__.split(".")[0]
