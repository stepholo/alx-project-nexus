from .views import OrderViewSet, OrderItemViewSet
from django.urls import path


urlpatterns = [
    path(
        'orders/',
        OrderViewSet.as_view({'get': 'list'}),
        name='order-list'
        ),
    path(
        'orders/checkout/',
        OrderViewSet.as_view({
            'post': 'checkout'
            }),
        name='order-checkout'
    ),
    path(
        'order-items/',
        OrderItemViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='order-item-list'
    ),
    path(
        'order-items/<int:id>/',
        OrderItemViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'patch': 'partial_update', 'delete': 'destroy'
            }),
        name='order-item-detail'
        ),
]
