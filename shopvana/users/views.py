from .serializers import UserSerializer
from .models import User
from utils.email import send_notification_email
from rest_framework import viewsets, permissions, filters
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
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

    def perform_create(self, serializer: UserSerializer) -> None:
        """
        Save the new user instance and send a welcome email.
        """
        user = serializer.save()
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'activation_url': f"{self.request.scheme}://{self.request.get_host()}/activate/{user.activation_token}/"
        }

        send_notification_email(
            subject='Welcome to Our Store!',
            template_name='template/emails/account_activation.html',
            context=context,
            to_email=user.email
        )
