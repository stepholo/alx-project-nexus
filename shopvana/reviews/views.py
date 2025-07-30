from .models import Review
from .serializers import ReviewSerializer
from rest_framework import viewsets


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for handling product reviews."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def perform_create(self, serializer: ReviewSerializer) -> None:
        """Override to set the user_id from the request user."""
        serializer.save(user_id=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.kwargs.get('product')
        user_id = self.kwargs.get('user')

        if product_id and user_id:
            return queryset.filter(product_id=product_id, user_id=user_id)
        elif product_id:
            return queryset.filter(product_id=product_id)
        elif user_id:
            return queryset.filter(user_id=user_id)
        return queryset

    def get_serializer_context(self) -> dict:
        """Add additional context to the serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
