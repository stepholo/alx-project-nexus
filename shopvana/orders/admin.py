from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model."""
    list_display = ('order_id', 'user', 'status', 'ordered_at')
    search_fields = ('user__username',)
    list_filter = ('status', 'ordered_at')
    ordering = ('-ordered_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('ordered_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model."""
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__user__username', 'product__name')
    raw_id_fields = ('order', 'product')
    autocomplete_fields = ('order', 'product')
    ordering = ('order', 'product')
    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'quantity')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Override save_model to set the price based on the product."""
        if not change:
            obj.price = obj.product.price
        super().save_model(request, obj, form, change)
        obj.save()

    def get_queryset(self, request):
        """Override get_queryset to prefetch related objects for performance."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'product')
