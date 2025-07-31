from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for managing payments."""
    list_display = ('transaction_id', 'order', 'amount', 'currency', 'status', 'payment_method', 'created_at')
    search_fields = ('order__id', 'status')
    list_filter = ('status', 'created_at')
    readonly_fields = ('transaction_id', 'created_at')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('transaction_id', 'order', 'amount', 'status', 'created_at')
        }),
    )
