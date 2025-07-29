from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from uuid import uuid4


class User(AbstractUser):
    """Custom user model for Shopvana."""
    user_id = models.UUIDField(
        default=uuid4,
        editable=False,
        unique=True,
        primary_key=True,
        help_text="Unique identifier for the user."
    )
    email = models.EmailField(
        unique=True,
        help_text="Email address of the user."
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="First name of the user."
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="Last name of the user."
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Unique username for the user."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether the user account is active."
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Indicates whether the user can log into the admin site."
    )
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='customer',
        help_text="Role of the user in the system."
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the user joined."
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time of the user's last login."
    )
    password = models.CharField(
        max_length=128,
        help_text="Password for the user account."
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="Profile picture of the user."
    )

    groups = models.ManyToManyField(
        Group,
        related_name='shopvana_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='shopvana_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        """Return a string representation of the user."""
        return f'{self.first_name} {self.last_name} ({self.email})'

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email'], name='user_email_idx'),
            models.Index(fields=['date_joined'], name='user_date_joined_idx'),
            models.Index(fields=['role'], name='user_role_idx'),
            models.Index(fields=['username'], name='user_username_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['email'], name='unique_user_email'),
            models.UniqueConstraint(
                fields=['username'], name='unique_user_username'),
        ]
