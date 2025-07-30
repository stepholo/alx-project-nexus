from .models import Review
from rest_framework import serializers


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model."""

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('review_id', 'created_at', 'updated_at')
        extra_kwargs = {
            'rating': {'min_value': 1, 'max_value': 5},
            'comment': {'required': False, 'allow_blank': True}
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('product_id', 'user_id'),
                message="You have already reviewed this product."
            )
        ]
