from .views import CategoryViewSet, ProductViewSet
from django.urls import path


urlpatterns = [
    path(
        'categories/',
        CategoryViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='category-list'
    ),
    path(
        'categories/<int:pk>/',
        CategoryViewSet.as_view({'get': 'retrieve',
                                 'put': 'update',
                                 'delete': 'destroy'}),
        name='category-detail'
    ),
    path(
        'products/',
        ProductViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='product-list'
    ),
    path(
        'products/<int:pk>/',
        ProductViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'delete': 'destroy'
            }),
        name='product-detail'
        ),
]
