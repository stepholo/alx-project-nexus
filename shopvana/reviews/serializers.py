from .models import Review
from rest_framework import serializers
from orders.models import OrderItem


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model."""
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=OrderItem.objects.all(),
        required=True
    )

    class Meta:
        model = Review
        fields = ['review_id', 'order_id', 'user_id', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ('review_id', 'user_id', 'created_at', 'updated_at')
        extra_kwargs = {
            'rating': {'min_value': 1, 'max_value': 5},
            'comment': {'required': False, 'allow_blank': True}
        }

    def validate_rating(self, value: int) -> int:
        """Validate that the rating is an int and is between 1 and 5."""
        if not isinstance(value, int):
            raise serializers.ValidationError("Rating must be an integer.")
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
                )
        return value
