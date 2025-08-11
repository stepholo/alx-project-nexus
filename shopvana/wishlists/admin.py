from django.contrib import admin
from .models import Wishlist, WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin interface for managing Wishlist Items."""
    list_display = (
        'item_id', 'wishlist_name', 'product',
        'user_name', 'added_on', 'updated_at'
        )
    search_fields = ('wishlist__name', 'product__name', 'user__username')
    list_filter = ('added_on', 'wishlist__name')
    ordering = ('-added_on',)
    readonly_fields = ('item_id', 'added_on', 'updated_at')

    def wishlist_name(self, obj):
        """Display the name of the wishlist."""
        return obj.wishlist.name
    wishlist_name.short_description = 'Wishlist Name'

    def user_name(self, obj):
        """Display the username of the user."""
        return obj.user.username
    user_name.short_description = 'User Name'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin interface for managing Wishlists."""
    list_display = ('user_name', 'name', 'added_on', 'updated_at')
    search_fields = ('name', 'user__username')
    list_filter = ('added_on', 'name')
    ordering = ('-added_on',)
    readonly_fields = ('wishlist_id', 'added_on', 'updated_at')

    def user_name(self, obj):
        """Display the username of the user."""
        return obj.user.username
    user_name.short_description = 'User Name'
