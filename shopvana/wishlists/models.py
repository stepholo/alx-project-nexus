from django.db import models
from uuid import uuid4


class Wishlist(models.Model):
    """Model representing a user's wishlist."""
    wishlist_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
        )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='wishlists'
        )
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='wishlists'
        )
    name = models.CharField(max_length=255, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Wishlist {self.wishlist_id} for User {self.user.username}"

    class Meta:
        verbose_name_plural = "Wishlists"
        ordering = ['-added_on']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['added_on']),
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_wishlist_item_per_user'
            )
        ]


class WishlistItem(models.Model):
    """Model representing an item in a user's wishlist."""
    item_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
        )
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name='items'
        )
    product_id = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='wishlist_items'
        )
    user_id = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='wishlist_items'
        )
    added_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Item {self.product_id} in {self.wishlist.product.name} Wishlist"

    class Meta:
        verbose_name_plural = "Wishlist Items"
        ordering = ['-added_on']
        indexes = [
            models.Index(fields=['wishlist']),
            models.Index(fields=['product_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['added_on']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'product_id'],
                name='unique_wishlist_item_per_wishlist'
            )
        ]
