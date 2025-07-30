from .models import CartItem
from .serializers import CartItemSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CartItemViewSet(viewsets.ModelViewSet):
    """Viewset for managing Cart Item"""

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Custom behavior on create."""
        serializer.save()

    def perform_update(self, serializer):
        """Custom behavior on update."""
        serializer.save()

    def perform_destroy(self, instance):
        """Custom behavior on delete."""
        instance.delete()
