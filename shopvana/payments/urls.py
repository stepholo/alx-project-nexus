from .views import PaymentViewSet, MpesaCallbackView
from django.urls import path
from rest_framework.routers import DefaultRouter

"""Payment URLs for the Shopvana application.
This module defines the URL patterns for the Payment API endpoints,
allowing clients to interact with payment resources.
"""

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path(
        'payments/',
        PaymentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='payment-list'
        ),
    path(
        'payments/<uuid:pk>/',
        PaymentViewSet.as_view({
            'get': 'retrieve',
            }),
        name='payment-detail'
        ),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),
] + router.urls
