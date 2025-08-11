from django.db import models
from uuid import uuid4


class CartItem(models.Model):
    """Model representing an item in the shopping cart."""
    cart_id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        ordering = ['-added_at']
        db_table = 'shopvana_cart_item'
        indexes = [
            models.Index(fields=['user', 'product']),
            models.Index(fields=['-added_at']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_cart_item')
        ]

    @property
    def id(self):
        """Return the cart item ID."""
        return self.cart_id

    @property
    def total_price(self):
        """Calculate the total price for this cart item."""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user} - {self.product} ({self.quantity})"
