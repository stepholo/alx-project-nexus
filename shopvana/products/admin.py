from django.contrib import admin
from .models import Product, Category
from django.utils import timezone


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for managing products."""
    list_display = (
        'product_id', 'name', 'description',
        'price', 'image', 'stock_quantity',
        'is_active', 'created_at'
        )
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'category')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        """Override to use custom manager for active products."""
        return Product.objects.active_products()

    def save_model(self, request, obj, form, change):
        """Custom save method to handle stock updates."""
        if change:
            # If the product is being updated, check stock changes
            original = Product.objects.get(pk=obj.pk)
            if original.stock_quantity != obj.stock_quantity:
                # Handle stock changes if necessary
                obj.updated_at = timezone.now()
                print(
                    f"Stock updated for {obj.name}: {original.stock_quantity} -> {obj.stock_quantity}"
                )
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for managing product categories."""
    list_display = ('name', 'category_id', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        """Override to use custom manager for active categories."""
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        """Custom save method to handle category updates."""
        super().save_model(request, obj, form, change)
        obj.updated_at = timezone.now()
