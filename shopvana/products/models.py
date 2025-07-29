from django.db import models
from uuid import uuid4


# Adding a custom manager for product queries
class ProductManager(models.Manager):
    """Custom manager for Product model to handle common queries."""

    def active_products(self):
        """Return all active products."""
        return self.filter(is_active=True)

    def products_in_category(self, category):
        """Return products in a specific category."""
        return self.filter(category=category, is_active=True)

    def search_products(self, query):
        """Search for products by name or description."""
        return self.filter(
            models.Q(
                name__icontains=query
                ) | models.Q(description__icontains=query),
            is_active=True
        )


# Adding a custom manager for category queries
class CategoryManager(models.Manager):
    """Custom manager for Category model to handle common queries."""
    def active_categories(self):
        """Return all categories that have active products."""
        return self.filter(products__is_active=True).distinct()

    def get_subcategories(self, category):
        """Return subcategories of a given category."""
        return self.filter(parent_category=category)


class Category(models.Model):
    """Model representing a product category."""
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Parent category for subcategories"
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the category"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the category"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the category was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the category was last updated"
    )

    objects = CategoryManager()  # <-- define inside the class

    def __str__(self):
        """String representation of the category."""
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]


class Product(models.Model):
    """Model representing a product in the shop."""
    product_id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        unique=True,
        editable=False,
        help_text="Unique identifier for the product"
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the product"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the product"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price of the product"
    )
    image = models.ImageField(
        upload_to='products/pictures/',
        blank=True,
        help_text="Image of the product"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the product was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the product was last updated"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Quantity of the product in stock"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the product is active and available for sale"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Category to which the product belongs"
    )

    objects = ProductManager()

    def __str__(self):
        """String representation of the product."""
        return self.name

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['name']
        # Adding indexes for better query performance
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['category']),
        ]
        # Adding constraints to ensure data integrity
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_gte_0'
            ),
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name='stock_quantity_gte_0'
            )
        ]

        # Adding unique constraint to ensure product
        # names are unique within a category
        unique_together = (('name', 'category'),)
