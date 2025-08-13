from .views import UserViewSet, RegisterView, ActivateAccountView
from django.urls import path

# This file defines the URL patterns for the user management API.

urlpatterns = [
    path('users/', UserViewSet.as_view(
        {'get': 'list'}),
        name='user-list'),
    path('users/<uuid:id>/', UserViewSet.as_view(
        {'get': 'retrieve'}),
        name='user-detail'),
    path('users/register/', RegisterView.as_view(), name='user-register'),
    path('users/activate/<uuid:activation_token>/', ActivateAccountView.as_view(), name='user-activate'),

]
