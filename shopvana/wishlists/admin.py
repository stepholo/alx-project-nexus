from django.contrib import admin
from .models import Wishlist, WishlistItem


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin interface for managing Wishlists."""
    list_display = ('wishlist_id', 'user', 'name', 'added_on', 'updated_at')
    search_fields = ('name', 'user__username')
    list_filter = ('added_on',)
    ordering = ('-added_on',)
    readonly_fields = ('wishlist_id', 'added_on', 'updated_at')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin interface for managing Wishlist Items."""
    list_display = ('item_id', 'wishlist', 'product_id', 'user_id', 'added_on', 'updated_at')
    search_fields = ('wishlist__name', 'product_id__name', 'user_id__username')
    list_filter = ('added_on',)
    ordering = ('-added_on',)
    readonly_fields = ('item_id', 'added_on', 'updated_at')
