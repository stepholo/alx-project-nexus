from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import OrderItem
from products.models import Product


@receiver(post_save, sender=OrderItem)
def update_product_stock(sender, instance, created, **kwargs):
    """Signal to update product stock when an OrderItem is saved."""
    if created:
        # Decrease stock when an order item is created
        instance.product.stock_quantity -= instance.quantity
        instance.product.save()
    else:
        # If the order item is updated, adjust stock accordingly
        original_quantity = instance.__class__.objects.get(pk=instance.pk).quantity
        instance.product.stock_quantity += original_quantity - instance.quantity
        instance.product.save()
