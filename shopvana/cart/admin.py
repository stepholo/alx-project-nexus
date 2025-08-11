from django.contrib import admin
from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for CartItem model."""
    list_display = ('cart_id', 'product', 'quantity', 'added_at')
    search_fields = ['product__name']
    list_filter = ['product']
    autocomplete_fields = ['product']
    ordering = ['product']
    fieldsets = ((None, {
            'fields': ('product', 'quantity')
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
        return qs.select_related('product')
