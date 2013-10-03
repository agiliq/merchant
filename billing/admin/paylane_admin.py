from django.contrib import admin
from billing.models.paylane_models import *

class PaylaneTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'transaction_date', 'amount', 'success', 'error_code')
    list_filter = ('success',)
    ordering = ('-transaction_date',)
    search_fields = ['customer_name', 'customer_email']

admin.site.register(PaylaneTransaction, PaylaneTransactionAdmin)

