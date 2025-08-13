from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Order
from typing import Type

@receiver(pre_delete, sender=Order)
def restore_stock_on_order_delete(sender: Type[Order], instance: Order, **kwargs) -> None:
    """Lock the stock restoration"""
    for item in instance.items.all():
        product = item.product
        product.stock_quantity += item.quantity
        product.is_active = product.stock_quantity > 0
        product.save()
