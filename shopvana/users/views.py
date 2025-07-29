from .serializers import UserSerializer
from .models import User
from rest_framework import viewsets, permissions, filters


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        """
        Optionally restricts the returned users to a given role,
        by filtering against a `role` query parameter in the URL.
        """
        queryset = self.queryset
        role = self.request.query_params.get('role', None)
        if role is not None:
            queryset = queryset.filter(role=role)
        return queryset
