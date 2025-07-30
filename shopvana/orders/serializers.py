from .models import Order, OrderItem
from rest_framework import serializers
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""

    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_purchase']
        read_only_fields = ['id', 'product', 'price_at_purchase']

    def create(self, validated_data):
        """Create a new OrderItem instance."""
        return OrderItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing OrderItem instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_quantity(self, value):
        """Ensure quantity is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be a positive integer."
                )
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_id', 'user', 'total_amount',
            'status', 'shipping_address', 'ordered_at', 'items'
            ]
        read_only_fields = [
            'order_id', 'user', 'total_amount', 'status', 'ordered_at'
            ]
        extra_kwargs = {
            'shipping_address': {'required': True},
            'status': {'default': 'pending'}
        }

    def create(self, validated_data):
        """Create a new Order instance."""
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        """Update an existing Order instance."""
        items_data = validated_data.pop('items', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update order items
        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id:
                item = OrderItem.objects.get(id=item_id, order=instance)
                for attr, value in item_data.items():
                    setattr(item, attr, value)
                item.save()
            else:
                OrderItem.objects.create(order=instance, **item_data)

        return instance

    def validate_shipping_address(self, value):
        """Ensure shipping address is not empty."""
        if not value:
            raise serializers.ValidationError(
                "Shipping address cannot be empty."
                )
        return value

    def validate_status(self, value):
        """Ensure status is a valid choice."""
        valid_statuses = dict(Order.STATUS_CHOICES).keys()
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of {', '.join(valid_statuses)}."
                )
        return value

    def to_representation(self, instance):
        """Customize the representation of the Order instance."""
        representation = super().to_representation(instance)
        representation['items'] = OrderItemSerializer(
            instance.items.all(), many=True).data
        return representation
