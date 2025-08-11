from .models import Wishlist, WishlistItem
from products.models import Product
from products.serializers import ProductSerializer
from rest_framework import serializers


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model."""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        help_text="The user who owns the wishlist"
    )
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Wishlist
        fields = ['wishlist_id', 'name', 'user_id', 'added_on', 'updated_at', 'user']
        read_only_fields = ['wishlist_id', 'added_on', 'updated_at', 'user_id']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Wishlist.objects.all(),
                fields=('user', 'name'),
                message="A wishlist with this name already exists for this user."
            )
        ]

    def validate_name(self, value: str) -> str:
        """Validate that the wishlist name is not empty and does not exceed 100 characters."""
        if not value:
            raise serializers.ValidationError("Wishlist name cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Wishlist name cannot exceed 100 characters.")
        return value


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for WishlistItem model."""

    user_id = serializers.ReadOnlyField(source='user.id')
    user_name = serializers.ReadOnlyField(source='user.username')  # New
    wishlist_name = serializers.ReadOnlyField(source='wishlist.name')  # New
    product_name = serializers.ReadOnlyField(source='product.name')
    wishlist = serializers.PrimaryKeyRelatedField(
        queryset=Wishlist.objects.all(),
        help_text="Select wishlist by ID"
    )
    product = ProductSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        help_text="Select product by ID"
    )

    class Meta:
        model = WishlistItem
        fields = ['item_id', 'wishlist', 'wishlist_name',
                  'product', 'product_name', 'user_id',
                  'user_name', 'added_on', 'updated_at']
        read_only_fields = ['item_id', 'added_on', 'updated_at', 'user_id',
                            'user_name', 'wishlist_name', 'product_name']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=WishlistItem.objects.all(),
                fields=('wishlist', 'product'),
                message="This product is already in the wishlist."
            )
        ]

    def validate(self, attrs):
        """Ensure that the wishlist belongs to the user."""
        request = self.context.get('request')
        user = request.user if request else None
        if user and attrs['wishlist'].user != user:
            raise serializers.ValidationError("This wishlist does not belong to the user.")
        return attrs

    def create(self, validated_data):
        """Set the user to the current authenticated user before saving."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Ensure user cannot be changed on update."""
        validated_data.pop('user_id', None)
        return super().update(instance, validated_data)
