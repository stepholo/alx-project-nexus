from .serializers import UserSerializer, RegistrationSerializer
from .models import User
from utils.email import send_notification_email
from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse
from utils.permissions import EcommercePermission
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = [EcommercePermission]
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
        activation_path = reverse('user-activate', kwargs={'activation_token': user.activation_token})
        activation_link = f"{self.request.scheme}://{self.request.get_host()}{activation_path}"
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'activation_link': activation_link
        }

        send_notification_email(
            subject='Welcome to Our Store!',
            template_name='emails/account_activation.html',
            context=context,
            to_email=user.email
        )


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer: UserSerializer) -> None:
        """
        Save the new user instance and send a welcome email.
        """
        user = serializer.save()
        activation_path = reverse('user-activate', kwargs={'activation_token': user.activation_token})
        activation_link = f"{self.request.scheme}://{self.request.get_host()}{activation_path}"
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'activation_link': activation_link
        }

        send_notification_email(
            subject='Welcome to Our Store!',
            template_name='emails/account_activation.html',
            context=context,
            to_email=user.email
        )


class ActivateAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, activation_token):
        try:
            user = User.objects.get(activation_token=activation_token)
            if user.is_active:
                return Response({'message': 'Account already activated.'}, status=status.HTTP_200_OK)
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully!'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Invalid activation link.'}, status=status.HTTP_404_NOT_FOUND)
