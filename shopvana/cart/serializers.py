from rest_framework import serializers
from products.serializers import ProductSerializer
from users.serializers import UserSerializer
from products.models import Product
from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        help_text="Product ID to add to cart."
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    product_name = serializers.ReadOnlyField(source='product.name')
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, obj):
        """Calculate the total price for this cart item."""
        return obj.total_price

    class Meta:
        model = CartItem
        fields = [
            'cart_id', 'product',
            'user', 'product_name', 'quantity',
            'total_price',
            'added_at', 'updated_at'
        ]
        read_only_fields = ['cart_id', 'added_at', 'product_name', 'updated_at']

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        user = self.context['request'].user

        # Get existing quantity if this item is already in cart
        existing_item = CartItem.objects.filter(user=user, product=product).first()
        existing_quantity = existing_item.quantity if existing_item else 0

        total_quantity = existing_quantity + quantity

        if total_quantity > product.stock_quantity:
            raise serializers.ValidationError(
                f"Cannot add {quantity} items to cart. Only {product.stock_quantity - existing_quantity} left in stock."
            )
        return attrs

    def validate_quantity(self, value):
        """Validate that quantity is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def create(self, validated_data):
        return CartItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance
