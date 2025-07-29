from .models import Category, Product
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'parent_category': {'required': False, 'allow_null': True}
        }
        depth = 1
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['name'],
                message="Category with this name already exists."
            )
        ]

        def validate_parent_category(self, value: Category) -> Category:
            """Ensure that the parent category is not a child of itself."""
            if value and value == self.instance:
                raise serializers.ValidationError(
                    "A category cannot be its own parent.")
            return value

        def validate_description(self, value: str) -> str:
            """Ensure that the description is not too long."""
            if len(value) > 1000:
                raise serializers.ValidationError(
                    "Description is too long. Max length is 1000 characters.")
            return value

        def validate_name(self, value: str) -> str:
            """Ensure that the name is not too long."""
            if len(value) > 255:
                raise serializers.ValidationError(
                    "Name is too long. Maximum length is 255 characters.")
            return value

        def validate(self, attrs: dict) -> dict:
            """Ensure that the name is unique."""
            if Category.objects.filter(name=attrs['name']).exists():
                raise serializers.ValidationError(
                    "Category with this name already exists.")
            return attrs


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['product_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'category': {'required': True}
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields=['name'],
                message="Product with this name already exists."
            )
        ]

    def validate_name(self, value: str) -> str:
        """Ensure that the name is not too long."""
        if len(value) > 255:
            raise serializers.ValidationError(
                "Name is too long. Maximum length is 255 characters.")
        return value

    def validate_description(self, value: str) -> str:
        """Ensure that the description is not too long."""
        if len(value) > 1000:
            raise serializers.ValidationError(
                "Description is too long. Max length is 1000 characters.")
        return value

    def validate_price(self, value: float) -> float:
        """Ensure that the price is a positive number."""
        if value < 0:
            raise serializers.ValidationError(
                "Price must be a positive number.")
        return value

    def validate_stock_quantity(self, value: int) -> int:
        """Ensure that the stock quantity is a non-negative integer."""
        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity must be a non-negative integer.")
        return value

    def validate(self, attrs: dict) -> dict:
        """Ensure that the product name is unique within the category."""
        if Product.objects.filter(
                name=attrs['name'], category=attrs['category']).exists():
            raise serializers.ValidationError(
                "Product with this name already exists.")
        return attrs

    def to_representation(self, instance: Product) -> dict:
        """Customize the representation of the product."""
        represent = super().to_representation(instance)
        represent['category'] = CategorySerializer(instance.category).data
        return represent
