from django.db import models
from uuid import uuid4

STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
class Order(models.Model):
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

    def save(self, *args, **kwargs):
        """Override save to propagate status changes to OrderItems."""
        if not self._state.adding:  # Only propagate if the instance already exists (i.e., on update)
            original = Order.objects.get(pk=self.pk)
            if original.status != self.status:  # Status changed
                self.items.update(item_status=self.status)
        super().save(*args, **kwargs)

    @property
    def id(self):
        """Return the order ID."""
        return self.order_id

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-ordered_at']
        db_table = 'shopvana_order'
        indexes = [
            models.Index(fields=['ordered_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"Order {self.order_id} by {self.user.username} - {self.status}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        'Order', related_name='items', on_delete=models.CASCADE
        )
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    item_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
        )
    quantity = models.PositiveIntegerField()


    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        unique_together = ('order', 'product')
        db_table = 'shopvana_order_item'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]
        ordering = ['order', 'product']

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"
