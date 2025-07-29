from .models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'first_name', 'last_name', 'username',
            'is_active', 'is_staff', 'role', 'date_joined', 'last_login',
            'full_name'
        ]
        read_only_fields = ['user_id', 'date_joined', 'last_login']
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
            if User.objects.filter(email=value).exists():
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
            if User.objects.filter(username=value).exists():
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

        def create(self, validated_data: dict) -> User:
            """Overide create method to hash the password before saving."""
            validated_data['password'] = make_password(
                validated_data['password'])
            return super().create(validated_data)
