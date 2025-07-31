from .views import PaymentViewSet
from django.urls import path

"""Payment URLs for the Shopvana application.
This module defines the URL patterns for the Payment API endpoints,
allowing clients to interact with payment resources.
"""

urlpatterns = [
    path(
        'payments/',
        PaymentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='payment-list'
        ),
    path(
        'payments/<uuid:pk>/',
        PaymentViewSet.as_view({
            'get': 'retrieve', 'put': 'update',
            'delete': 'destroy'
            }),
        name='payment-detail'
        ),
]
