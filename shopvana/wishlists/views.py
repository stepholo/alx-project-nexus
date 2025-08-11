from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer
from rest_framework import viewsets


class WishlistViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user wishlists."""
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self) -> dict:
        """Return wishlists for the authenticated user."""
        user = self.request.user
        return Wishlist.objects.filter(user=user.id)

    def perform_create(self, serializer: WishlistSerializer) -> None:
        """Set the user_id to the authenticated user when creating a wishlist."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer: WishlistSerializer) -> None:
        """Update the wishlist while ensuring the user_id remains the authenticated user."""
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance: Wishlist) -> None:
        """Delete the wishlist only if it belongs to the authenticated user."""
        if instance.user_id == self.request.user:
            instance.delete()
        else:
            raise PermissionError("You do not have permission to delete this wishlist.")


class WishlistItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing items in user wishlists."""
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer

    def get_queryset(self) -> dict:
        """Return wishlist items for the authenticated user."""
        user = self.request.user
        return WishlistItem.objects.filter(user=user.id)

    def perform_create(self, serializer: WishlistItemSerializer) -> None:
        """Set the user_id to the authenticated user when creating a wishlist item."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer: WishlistItemSerializer) -> None:
        """Update the wishlist item while ensuring the user_id remains the authenticated user."""
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance: WishlistItem) -> None:
        """Delete the wishlist item only if it belongs to the authenticated user."""
        if instance.user.id == self.request.user.id:
            instance.delete()
        else:
            raise PermissionError("You do not have permission to delete this wishlist item.")
