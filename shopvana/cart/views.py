from rest_framework import viewsets
from utils.permissions import EcommercePermission
from .models import CartItem
from .serializers import CartItemSerializer
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(tags=["Customer's Preference"])
class CartItemViewSet(viewsets.ModelViewSet):
    """Viewset for managing Cart Items"""
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [EcommercePermission]

    def get_queryset(self):
        # Return only cart items for the authenticated user
            if not self.request.user.is_authenticated:
                return CartItem.objects.none()  # Empty queryset for anonymous users
            return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Auto-increment quantity if the item already exists in cart"""
        user = self.request.user
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        existing_item = CartItem.objects.filter(user=user, product=product).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            serializer.save(user=user)
