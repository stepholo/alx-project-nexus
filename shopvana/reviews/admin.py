from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for managing product reviews."""
    list_display = ('review_id', 'order_id', 'user_id', 'rating', 'created_at')
    search_fields = ('order__id', 'user__username', 'rating')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('review_id', 'created_at')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': (
                'review_id', 'product', 'user',
                'rating', 'comment', 'created_at'
                )
        }),
    )
