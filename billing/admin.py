from django.contrib import admin
import billing.models as billing_models

admin.site.register(billing_models.GCNewOrderNotification)
admin.site.register(billing_models.AuthorizeAIMResponse)
admin.site.register(billing_models.WorldPayResponse)
admin.site.register(billing_models.AmazonFPSResponse)


class PaylaneTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'transaction_date', 'amount', 'success', 'error_code')
    list_filter = ('success',)
    ordering = ('-transaction_date',)
    search_fields = ['customer_name', 'customer_email']

admin.site.register(billing_models.PaylaneTransaction, PaylaneTransactionAdmin)
