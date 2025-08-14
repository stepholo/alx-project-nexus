from .models import Order, OrderItem
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
from uuid import uuid4
import requests
from utils.permissions import EcommercePermission
from rest_framework import status
from cart.models import CartItem
from products.models import Product
from payments.models import Payment
from utils.email import send_notification_email
from .serializers import OrderSerializer, OrderItemSerializer
import logging
from drf_yasg.utils import swagger_auto_schema

# Chapa Credentials
CHAPA_API_URL = f"{settings.CHAPA_BASE_URL.rstrip('/')}/transaction/initialize"
CHAPA_VERIFY_URL = f"{settings.CHAPA_BASE_URL}/transaction/verify/"
CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY

@swagger_auto_schema(tags=["Customer's Preference"])
class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [EcommercePermission]

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

        order.mark_ready_for_payment(minutes_valid=60)  # Mark order ready for payment

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

        # Send order confirmation email
        order_items_list = []
        for item in order.items.select_related('product'):
            order_items_list.append({
                'name': item.product.name,
                'price': item.product.price,
                'quantity': item.quantity,
                'subtotal': item.quantity * item.product.price
            })

        context = {
            'customer_name': user.get_full_name(),
            'order_id': order.id,
            'order_total': order.total_amount,
            'shipping_address': order.shipping_address,
            'status': order.status,
            'ordered_at': order.ordered_at,
            'items': order_items_list
        }
        send_notification_email(
            subject='Order Confirmation',
            template_name='emails/order_confirmation.html',
            context=context,
            to_email=user.email,
        )

        # === Initiate payment with Chapa ===
        order_id_short = str(order.order_id)[:8]
        user_id_short = str(user.id)[:4]
        random_part = uuid4().hex[:8]
        tx_ref = f"o{order_id_short}u{user_id_short}{random_part}"

        callback_url = f"{settings.SITE_URL}/api/payments/verify/"
        logging.info(f"Call back URL: {callback_url}")
        payload = {
            "amount": str(total_amount),
            "currency": "ETB",  # or your preferred currency
            "email": user.email,
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "payment_method": "chapa",
        }
        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
        chapa_resp = requests.post(CHAPA_API_URL, json=payload, headers=headers)
        logging.info(f"Chapa response: {chapa_resp.status_code} - {chapa_resp.text}")

        checkout_url = None
        if chapa_resp.status_code == 200:
            resp_data = chapa_resp.json()
            checkout_url = resp_data['data']['checkout_url']
            logging.info(f"Chapa checkout URL: {checkout_url}")

            # Save Payment record
            Payment.objects.create(
                order=order,
                user=user,
                chapa_tx_ref=tx_ref,
                amount=total_amount,
                currency="ETB",
                status="pending",
                payment_method="chapa",
            )

            # Send payment link email
            send_notification_email(
                to_email=user.email,
                subject="Complete Your Payment",
                template_name="emails/checkout_email.html",
                context={
                    "user_name": user.get_full_name() or user.username,
                    "checkout_url": checkout_url,
                    "payment_window": order.payment_window_expires_at,
                }
            )



        serializer = self.get_serializer(order)
        return Response({
            "order": serializer.data,
            "checkout_url": checkout_url
        }, status=status.HTTP_201_CREATED)

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
    permission_classes = [EcommercePermission]

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