from .models import Order, OrderItem
from rest_framework import viewsets
from .serializers import OrderSerializer, OrderItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def perform_create(self, serializer):
        """Override to set the user from the request."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Override to handle updates."""
        serializer.save()

    def perform_destroy(self, instance):
        """Override to handle order deletion."""
        instance.delete()


class OrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing order items."""

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def perform_create(self, serializer):
        """Override to set the order from the request."""
        serializer.save()

    def perform_update(self, serializer):
        """Override to handle updates."""
        serializer.save()

    def perform_destroy(self, instance):
        """Override to handle order item deletion."""
        instance.delete()
