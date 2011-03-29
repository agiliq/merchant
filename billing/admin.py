
from django.contrib import admin

import billing.models as billing_models

admin.site.register(billing_models.GCNewOrderNotification)
admin.site.register(billing_models.AuthorizeAIMResponse)
admin.site.register(billing_models.WorldPayResponse)
admin.site.register(billing_models.AmazonFPSResponse)
