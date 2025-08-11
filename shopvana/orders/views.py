from .models import Order, OrderItem
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status
from cart.models import CartItem
from products.models import Product
from utils.email import send_notification_email
from .serializers import OrderSerializer, OrderItemSerializer
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(tags=["Customer's Preference"])
class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    @action(detail=False, methods=['post'], url_path='checkout')
    @transaction.atomic
    def checkout(self, request):
        user = request.user
        cart_items = CartItem.objects.select_related('product').filter(user=user)

        if not cart_items.exists():
            return Response({'detail': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lock the products in the cart to prevent race conditions
        product_ids = [item.product.product_id for item in cart_items]
        products = Product.objects.select_for_update().filter(product_id__in=product_ids)
        product_map = {product.product_id: product for product in products}

        total_amount = 0
        stock_updates = []  # Track products to update

        # Validate stock availability
        for item in cart_items:
            product = product_map.get(item.product.product_id)
            if not product:
                return Response(
                    {"detail": f"Product {item.product.name} not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_stock = product.stock_quantity - item.quantity
            if new_stock < 0:
                return Response(
                    {"detail": f"Product {item.product.name} is oversold. Available stock: {product.stock_quantity}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            total_amount += item.quantity * product.price
            stock_updates.append((product, new_stock))

        # Get shipping address
        shipping_address = request.data.get('shipping_address')
        if not shipping_address:
            return Response({"detail": "Shipping address is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            shipping_address=shipping_address,
            status='pending'
        )

        # Create order items and update stock
        for item in cart_items:
            product, new_stock = next((p, ns) for p, ns in stock_updates if p.product_id == item.product.product_id)

            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity
            )

            # Update stock and is_active
            product.stock_quantity = new_stock
            product.is_active = new_stock > 0
            product.save()

        # Clear cart
        cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """Override to set the user from the request."""
        serializer.save(user=self.request.user)
        context = {
            'customer_name': self.request.user.get_full_name(),
            'order_id': serializer.instance.id,
            'order_total': serializer.instance.total_amount,
            'shipping_address': serializer.instance.shipping_address,
            'status': serializer.instance.status,
            'ordered_at': serializer.instance.ordered_at,
            'items': serializer.instance.items.all(),
        }

        send_notification_email(
            subject='Order Confirmation',
            template_name='template/emails/order_confirmation.html',
            context=context,
            recipient_list=[self.request.user.email]
        )

    def perform_update(self, serializer):
        """Override to handle updates."""
        serializer.save()

    def perform_destroy(self, instance):
        """Override to handle order deletion."""
        instance.delete()


@swagger_auto_schema(tags=["Customer's Preference"])
class OrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing order items."""

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    @transaction.atomic
    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        order = validated_data['order']
        product = validated_data['product']
        quantity = validated_data['quantity']

        # Lock the product to prevent race conditions
        product = Product.objects.select_for_update().get(product_id=product.product_id)

        # Validate stock
        new_stock = product.stock_quantity - quantity
        if new_stock < 0:
            return Response(
                {"detail": f"Product {product.name} is oversold. Available stock: {product.stock_quantity}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mirror order status to the order item
        order_item = serializer.save(item_status=order.status)

        # Update stock
        product.stock_quantity = new_stock
        product.is_active = new_stock > 0
        product.save()

        # Update order total_amount
        order.total_amount += quantity * product.price
        order.save()

        return Response(self.get_serializer(order_item).data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        """Override to handle updates."""
        serializer.save()

    @transaction.atomic
    def perform_destroy(self, instance):
        """Override to handle order item deletion with stock restoration."""
        product = instance.product
        quantity = instance.quantity
        order = instance.order

        # Lock the product to prevent race conditions
        product = Product.objects.select_for_update().get(product_id=product.product_id)

        # Restore stock
        product.stock_quantity += quantity
        product.is_active = product.stock_quantity > 0
        product.save()

        # Update order total_amount
        order.total_amount -= quantity * product.price
        if order.total_amount < 0:
            order.total_amount = 0  # Prevent negative total_amount
        order.save()

        # Delete the order item
        instance.delete()

        # Check if order has any remaining items
        if not order.items.exists():
            order.delete()