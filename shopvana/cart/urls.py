from .views import CartItemViewSet
from django.urls import path

"""
URL configuration for the Cart app in Shopvana.
This module defines the URL patterns for the CartItemViewSet, allowing
clients to interact with cart items via RESTful endpoints.
Each URL pattern corresponds to a specific action on the cart items,
"""

urlpatterns = [
    path(
        'cart-items/',
        CartItemViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='cart-item-list'
        ),
    path(
        'cart-items/<uuid:pk>/',
        CartItemViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'delete': 'destroy'
            }),
        name='cart-item-detail'
        ),
]
