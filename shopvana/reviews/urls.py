from .views import ReviewViewSet
from django.urls import path

"""
This file defines the URL patterns for the reviews app,
mapping URLs to the ReviewViewSet methods.
"""

urlpatterns = [
    path(
        'reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='review-list'
        ),
    path(
        'reviews/<uuid:pk>/',
        ReviewViewSet.as_view({
            'get': 'retrieve', 'put':
            'update', 'patch': 'partial_update',
            'delete': 'destroy'
            }),
        name='review-detail'
        ),
    path(
        'reviews/product/<uuid:product_id>/',
        ReviewViewSet.as_view({'get': 'list'}),
        name='review-by-product'
        ),
    path(
        'reviews/user/<uuid:user_id>/',
        ReviewViewSet.as_view({'get': 'list'}),
        name='review-by-user'
        ),
    path(
        'reviews/<uuid:product_id>/user/<uuid:user_id>/',
        ReviewViewSet.as_view({'get': 'list'}),
        name='review-by-product-and-user'
        ),
]
