from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(tags=["Product Cartegory"])
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer: CategorySerializer) -> None:
        """Override to add custom behavior on create."""
        serializer.save()

    def perform_update(self, serializer: CategorySerializer) -> None:
        """Override to add custom behavior on update."""
        serializer.save()

    def perform_destroy(self, instance: Category) -> None:
        """Override to add custom behavior on delete."""
        instance.delete()


@swagger_auto_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'price', 'created_at', 'category']
    ordering_fields = ['name', 'price', 'created_at']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def perform_create(self, serializer: ProductSerializer) -> None:
        """Override to add custom behavior on create."""
        serializer.save()

    def perform_update(self, serializer: ProductSerializer) -> None:
        """Override to add custom behavior on update."""
        serializer.save()

    def perform_destroy(self, instance: Product) -> None:
        """Override to add custom behavior on delete."""
        instance.delete()
