from django.db import models
from uuid import uuid4


class Payment(models.Model):
    """
    Represents a payment transaction in the Shopvana system.
    This model captures details about the payment such as amount, currency,
    payment method, associated order, user information, and status.
    """
    transaction_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
        )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    payment_method = models.CharField(max_length=50, choices=[
        ('mpesa', 'mpesa'),
        ('wallet', 'wallet'),
    ])
    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE,
        related_name='payments'
        )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='payments'
        )
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ])
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def id(self):
        """Return the payment ID."""
        return self.transaction_id

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        db_table = 'shopvana_payment'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['order']),
            models.Index(fields=['currency']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['amount']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['transaction_id'], name='unique_transaction_id'
                ),
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='amount_positive'
            ),
            models.CheckConstraint(
                check=models.Q
                (status__in=['pending', 'completed', 'failed', 'refunded']
                 ),
                name='valid_status'
            ),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.status} - {self.amount} {self.currency}"
