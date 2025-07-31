from django.db import models
from uuid import uuid4


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    order_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
        )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
        )
    shipping_address = models.CharField(max_length=255)
    ordered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-ordered_at']
        indexes = [
            models.Index(fields=['ordered_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"Order {self.order_id} by {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        'Order', related_name='items', on_delete=models.CASCADE
        )
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        unique_together = ('order', 'product')
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]
        ordering = ['order', 'product']

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"
