from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone


class EcommercePermission(BasePermission):
    """
    - Admin: all access.
    - Registered user (non-admin):
        * wishlist, order, orderitem, cartitem, reviews → GET, POST, PUT, PATCH, DELETE
        * payment → GET and POST (POST only if user owns a pending order)
    - Unauthenticated: GET only.
    """

    FULL_ACCESS_APPS = ['wishlists', 'orders', 'orderitem', 'cart', 'reviews']
    POST_ONLY_APPS = ['payments']

    def has_permission(self, request, view):
        # Everyone can GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        # Admin: full access
        if user and user.is_staff:
            return True

        # Registered user
        if user and user.is_authenticated:
            return self._is_allowed_method(view, request)

        # Unauthenticated: no non-safe methods
        return False

    def _is_allowed_method(self, view, request):
        if hasattr(view, 'queryset') and view.queryset is not None:
            model = view.queryset.model
            app_label = model._meta.app_label.lower()

            # Full CRUD apps
            if app_label in self.FULL_ACCESS_APPS:
                return request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

            # Payment rules
            if app_label in self.POST_ONLY_APPS:
                if request.method == 'GET':
                    return True
                if request.method == 'POST':
                    return request.user.is_staff

        return False

    def _is_valid_payment_request(self, request):
        """
        Only allow POST if:
        - The 'order' field is provided
        - The order belongs to the user
        - The order is still pending
        """
        order_id = request.data.get('order')
        if not order_id:
            return False

        try:
            from orders.models import Order  # Import here to avoid circular import
            order_obj = Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return False

        # Must be pending
        if order_obj.status.lower() != 'pending':
            return False

        # Must be marked ready for payment
        if not order_obj.ready_for_payment:
            return False

        # Must be within payment window
        if order_obj.payment_window_expires_at and timezone.now() > order_obj.payment_window_expires_at:
            return False

        return True
