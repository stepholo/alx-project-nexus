from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Payment
from .serializer import PaymentSerializer
import requests
from django.conf import settings
import logging
from uuid import uuid4
from utils.permissions import EcommercePermission
from utils.email import send_notification_email
from django.shortcuts import redirect
from rest_framework.decorators import action
from payments.utils import verify_chapa_payment

logger = logging.getLogger(__name__)

# Chapa Credentials
CHAPA_API_URL = f"{settings.CHAPA_BASE_URL.rstrip('/')}/transaction/initialize"
CHAPA_VERIFY_URL = f"{settings.CHAPA_BASE_URL}/transaction/verify/"
CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [EcommercePermission]

    def create(self, request, *args, **kwargs):
          # Only admins can create payments manually
        if not request.user.is_staff:
            return Response(
                {'detail': 'Manual payment creation is not allowed. Please checkout to initiate payment.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_instance = serializer.validated_data.get('order')
        amount = serializer.validated_data.get('amount')
        payment_method = serializer.validated_data.get('payment_method')
        currency = serializer.validated_data.get('currency')

        if not order_instance or not amount or not payment_method:
            return Response(
                {'error': 'order, amount, and payment_method are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = order_instance

        # Prevent double payment for the same order
        if order.status == "paid":
            return Response({'error': 'Order has already been paid.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

        # Fix tx_ref length
        order_id_short = str(order.order_id)[:8]
        user_id_short = str(request.user.id)[:4]
        random_part = uuid4().hex[:8]
        tx_ref = f"o{order_id_short}u{user_id_short}{random_part}"

        # Fix callback_url (ensure SITE_URL is a valid URL in your settings)
        callback_url = f"{settings.SITE_URL}/api/payments/verify/"

        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": request.user.email,
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "payment_method": payment_method,
        }

        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
        chapa_resp = requests.post(CHAPA_API_URL, json=payload, headers=headers)

        if chapa_resp.status_code == 200:
            resp_data = chapa_resp.json()
            Payment.objects.create(
                order=order,
                user=request.user,
                chapa_tx_ref=tx_ref,
                amount=amount,
                currency=currency,
                status="pending",
                payment_method=payment_method,
            )

            # Send checkout URL to user's email
            send_notification_email(
                to_email=request.user.email,
                subject="Complete Your Payment",
                template_name="emails/checkout_email.html",
                context={
                    "user_name": request.user.get_full_name() or request.user.username,
                    "checkout_url": resp_data['data']['checkout_url'],
                }
            )
            return Response({
                "checkout_url": resp_data['data']['checkout_url'],
                "tx_ref": tx_ref
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Chapa initiation failed: {chapa_resp.text}")
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='verify')
    def verify_payment(self, request):
        tx_ref = request.query_params.get('tx_ref')
        if not tx_ref:
            return Response({'error': 'tx_ref is required.'}, status=400)

        try:
            payment = Payment.objects.get(chapa_tx_ref=tx_ref, user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=404)

        status_str, receipt_url = verify_chapa_payment(payment)

        if status_str == "success" and receipt_url:
            return redirect(receipt_url)
        elif status_str == "success":
            return Response({'message': 'Payment verified successfully, but no receipt URL.'})
        elif status_str == "failed":
            return Response({'error': 'Payment failed.'}, status=400)
        else:
            return Response({'error': 'Verification request failed.'}, status=400)

    def retrieve(self, request, *args, **kwargs):
        tx_ref = request.query_params.get('tx_ref')
        try:
            payment = Payment.objects.get(chapa_tx_ref=tx_ref, user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=404)

        # No need to call Chapa API here; status is updated by Celery Beat
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
