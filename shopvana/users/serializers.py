from .models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    full_name = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        help_text="Password for the user account."
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'username',
            'is_active', 'is_staff', 'role', 'date_joined', 'last_login',
            'full_name', 'password', 'activation_token'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'activation_token']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj: User) -> str:
        """Return the full name of the user."""
        return f"{obj.first_name} {obj.last_name}".strip()

    def validate_email(self, value: str) -> str:
        """ Validates that the email ends with '.com' """
        if not value.endswith('.com'):
            raise serializers.ValidationError("Email must end with .com")
        if User.objects.filter(email=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError("Email already exists")
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        if value[0].isupper():
            raise serializers.ValidationError(
                "Email must start with an lowercase letter")
        if not value[0].isalpha():
            raise serializers.ValidationError(
                "Email must start with a letter")
        if '@' not in value:
            raise serializers.ValidationError("Email must contain '@'")
        return value

    def validate_username(self, value: str) -> str:
        """ Validates that the username is unique and not empty. """
        if not value:
            raise serializers.ValidationError("Username cannot be empty")
        if User.objects.filter(username=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError("Username already exists")
        if not value[0].isalpha():
            raise serializers.ValidationError(
                "Username must start with a letter")
        return value

    def validate_role_choice(self, value: str) -> str:
        """ Validates that the role is one of the predefined choices. """
        valid_roles = ['admin', 'customer', 'vendor']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Role must be one of {valid_roles}")
        return value

    def validate_password(self, value: str) -> str:
        """ Validates the password using Django's built-in validator. """
        validate_password(value, self.instance)
        return value

    def create(self, validated_data: dict) -> User:
        """Override create method to hash the password before saving."""
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """Override update method to hash the password if provided."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
