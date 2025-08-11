from .views import UserViewSet
from django.urls import path

# This file defines the URL patterns for the user management API.

urlpatterns = [
    path('users/', UserViewSet.as_view(
        {'get': 'list', 'post': 'create'}),
        name='user-list'),
    path('users/<uuid:id>/', UserViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='user-detail'),
]
