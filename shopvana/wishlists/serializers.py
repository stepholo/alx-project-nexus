from .models import Wishlist, WishlistItem
from rest_framework import serializers


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model."""

    class Meta:
        model = Wishlist
        fields = ['wishlist_id', 'name', 'user_id', 'added_on', 'updated_at']
        read_only_fields = ['wishlist_id', 'added_on', 'updated_at']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Wishlist.objects.all(),
                fields=('user_id', 'name'),
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

    class Meta:
        model = WishlistItem
        fields = ['item_id', 'wishlist', 'product_id', 'user_id', 'added_on', 'updated_at']
        read_only_fields = ['item_id', 'added_on', 'updated_at']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=WishlistItem.objects.all(),
                fields=('wishlist', 'product_id'),
                message="This product is already in the wishlist."
            )
        ]

    def validate(self, attrs):
        """Ensure that the wishlist belongs to the user."""
        if attrs['wishlist'].user_id != attrs['user_id']:
            raise serializers.ValidationError("This wishlist does not belong to the user.")
        return attrs
