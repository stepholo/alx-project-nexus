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

    def get_queryset(self) -> dict:
        """Filter reviews by product_id if provided in the query parameters."""
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return self.queryset.filter(product_id=product_id)
        return self.queryset

    def get_serializer_context(self) -> dict:
        """Add additional context to the serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
