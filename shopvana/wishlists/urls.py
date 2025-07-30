from .views import WishlistViewSet, WishlistItemViewSet
from django.urls import path

"""
This file defines the URL patterns for the wishlist app,
mapping URLs to both the whishlistviewset and wishlistItemviewset methods.
"""

urlpatterns = [
    path(
        'wishlists/',
        WishlistViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='wishlist-list'
        ),
    path('wishlists/<uuid:pk>/',
         WishlistViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
             }),
         name='wishlist-detail'
         ),
    path(
        'wishlist-items/',
        WishlistItemViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='wishlist-item-list'
        ),
    path(
        'wishlist-items/<uuid:pk>/',
        WishlistItemViewSet.as_view({
            'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
            }),
        name='wishlist-item-detail'
        ),
]
