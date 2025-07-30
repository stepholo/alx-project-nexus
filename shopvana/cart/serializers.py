from .models import CartItem
from rest_framework import serializers
from products.serializers import ProductSerializer
from users.serializers import UserSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['cart_id', 'user', 'product', 'added_at', 'updated_at']

    def create(self, validated_data):
        """Create a new cart item instance."""
        return CartItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing cart item instance."""
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance

    def delete(self, instance):
        """Delete a cart item instance."""
        instance.delete()
        return instance

    def validate_quantity(self, data):
        """Custom validation for cart item."""
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return data
