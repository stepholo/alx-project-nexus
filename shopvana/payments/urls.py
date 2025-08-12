from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
