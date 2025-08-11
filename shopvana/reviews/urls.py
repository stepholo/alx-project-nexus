from .views import ReviewViewSet
from django.urls import path

urlpatterns = [
    # Create/list reviews for a specific order item
    path(
        'order-items/reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='order-item-reviews'
    ),
    # Retrieve/update/delete a specific review
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
]
