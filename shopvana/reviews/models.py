from django.db import models
from uuid import uuid4


class Review(models.Model):
    """Model representing a product review."""
    review_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
    )
    product_id = models.ForeignKey(
        'products.Product',  # Update to the correct app and model
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user_id = models.ForeignKey(
        'users.User',  # Use Django's user model
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('product_id', 'user_id')
        indexes = [
            models.Index(fields=['product_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='rating_between_1_and_5'
            )
        ]

    def __str__(self):
        return f'Review {self.review_id} for Product {self.product_id}'