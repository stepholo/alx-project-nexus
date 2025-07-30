from .models import Payment
from rest_framework import viewsets
from .serializer import PaymentSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for handling Payment operations.
    This viewset provides CRUD operations for the Payment model, including
    listing, retrieving, creating, updating, and deleting payment records.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Override to add custom behavior on create."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Override to add custom behavior on update."""
        serializer.save()

    def perform_destroy(self, instance):
        """Override to add custom behavior on delete."""
        instance.delete()

    def get_queryset(self):
        """Override to filter queryset based on user."""
        user = self.request.user
        if user.is_authenticated:
            return self.queryset.filter(user=user)
        return self.queryset.none()
