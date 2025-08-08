from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD') or request.user.is_staff
