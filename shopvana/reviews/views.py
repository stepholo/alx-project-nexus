from .models import Review
from orders.models import OrderItem
from .serializers import ReviewSerializer
from rest_framework import viewsets, serializers


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for handling product reviews."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def perform_create(self, serializer: ReviewSerializer) -> None:
        """Allow reviews only for paid order items, one per user per item."""
        order_item = serializer.validated_data['order_id']

        if order_item.order.status != 'paid':
            raise serializers.ValidationError("You can only review items from paid orders.")

        if Review.objects.filter(order_id=order_item, user_id=self.request.user).exists():
            raise serializers.ValidationError("You have already reviewed this item.")

        serializer.save(
            user_id=self.request.user,
            order_id=order_item
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        id = self.kwargs.get('id')
        user_id = self.kwargs.get('user')

        if id and user_id:
            return queryset.filter(order_id=id, user_id=user_id)
        elif id:
            return queryset.filter(order_id=id)
        elif user_id:
            return queryset.filter(user_id=user_id)
        return queryset

    def get_serializer_context(self) -> dict:
        """Add additional context to the serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
