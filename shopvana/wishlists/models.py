from django.db import models
from uuid import uuid4


class Wishlist(models.Model):
    """Model representing a user's wishlist."""
    wishlist_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
        )
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='wishlists'
        )
    name = models.CharField(max_length=255, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Wishlist {self.wishlist_id} for User {self.user.username}"

    @property
    def id(self):
        return self.wishlist_id

    class Meta:
        verbose_name_plural = "Wishlists"
        ordering = ['-added_on']
        db_table = 'shopvana_wishlist'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['added_on']),
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
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
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='wishlist_items'
        )
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='wishlist_items'
        )
    added_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Item {self.product.name} in Wishlist '{self.wishlist.name}'"

    @property
    def id(self):
        return self.item_id

    class Meta:
        verbose_name_plural = "Wishlist Items"
        ordering = ['-added_on']
        db_table = 'shopvana_wishlist_item'
        indexes = [
            models.Index(fields=['wishlist']),
            models.Index(fields=['product']),
            models.Index(fields=['user']),
            models.Index(fields=['added_on']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'product'],
                name='unique_wishlist_item_per_wishlist'
            )
        ]
