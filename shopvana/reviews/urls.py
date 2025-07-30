from .views import ReviewViewSet
from django.urls import path

urlpatterns = [
    path(
        'reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='review-list'
    ),
    path(
        'reviews/<uuid:pk>/',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='review-detail'
    ),
    path(
        'reviews/product/<uuid:product>/',
        ReviewViewSet.as_view({'get': 'list'}),
        name='review-by-product'
    ),
    path(
        'reviews/user/<uuid:user>/',
        ReviewViewSet.as_view({'get': 'list'}),
        name='review-by-user'
    ),
    path(
        'reviews/<uuid:product>/user/<uuid:user>/',
        ReviewViewSet.as_view({'get': 'list'}),
        name='review-by-product-and-user'
    ),
]
