from .models import Payment
from rest_framework import viewsets
from .serializer import PaymentSerializer
from utils import tasks
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from .mpesa_client import stk_push_direct  # 🔹 Commented out real integration
from rest_framework.views import APIView
from rest_framework.response import Response
import logging
import uuid
from time import sleep
from drf_yasg.utils import swagger_auto_schema


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@swagger_auto_schema(tags=["Payments"])
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        order = serializer.validated_data.get('order')

        # Check if order already has a successful payment
        if Payment.objects.filter(order=order, status='completed').exists():
            raise serializers.ValidationError("This order has already been paid.")

        payment = serializer.save(user=self.request.user)

        if payment.payment_method == 'mpesa':
            # Simulate phone number normalization
            phone_number = self.request.data.get('phone_number')
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            phone_number = str(phone_number).lstrip('+')

            # if payment.amount != payment.order.total_amount:
            #     raise serializers.ValidationError("Payment amount must be equal to order total amount")

            logger.info(f"[SIMULATION] Initiating fake STK Push for {phone_number} amount {payment.amount}")

            # 🔹 Simulation mode instead of real stk_push_direct
            fake_checkout_id = str(uuid.uuid4())
            payment.checkout_request_id = fake_checkout_id
            payment.status = "pending"
            payment.save()
            tasks.simulate_payment_status_update.apply_async(args=[fake_checkout_id], countdown=3)

            logger.info(f"[SIMULATION] Fake STK Push created with CheckoutRequestID: {fake_checkout_id}")

            self.simulate_callback(fake_checkout_id)

        elif payment.payment_method == 'wallet':
            # Handle wallet payment logic
            if payment.amount > payment.wallet:
                raise serializers.ValidationError("Insufficient wallet balance")
            payment.wallet -= payment.amount
            payment.status = 'completed'
            payment.save()
            # Update order status on successful wallet payment
            order = payment.order
            order.status = 'paid'
            order.save()  # This will propagate to OrderItems via Order.save()
            logger.info(f"[WALLET] Payment {payment.id} completed using wallet balance. Order {order.id} set to 'paid'.")

    def simulate_callback(self, checkout_request_id):
        sleep(2)
        payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
        if not payment:
            logger.error(f"[SIMULATION] No payment found for CheckoutRequestID: {checkout_request_id}")
            return

        # Fail if amount doesn't match order total
        if payment.amount < payment.order.total_amount:
            result_code = 1
            result_desc = "Payment amount does not match order total"
        elif payment.amount >= payment.order.total_amount:
            result_code = 0
            result_desc = "The service request is processed successfully."

        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": str(uuid.uuid4()),
                    "CheckoutRequestID": checkout_request_id,
                    "ResultCode": result_code,
                    "ResultDesc": result_desc,
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "MpesaReceiptNumber", "Value": "SIM123ABC"},
                            {"Name": "Amount", "Value": float(payment.amount)},
                            {"Name": "PhoneNumber", "Value": "254700000000"},
                        ]
                    } if result_code == 0 else {}
                }
            }
        }

        logger.info(f"[SIMULATION] Sending simulated callback: {callback_data}")
        MpesaCallbackView().process_callback(callback_data)

@swagger_auto_schema(tags=["Payments"])
class MpesaCallbackView(APIView):
    permission_classes = []  # Open to M-Pesa servers (add IP whitelist later)

    def post(self, request):
        return self.process_callback(request.data)

    def process_callback(self, data):
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')

        try:
            payment = Payment.objects.get(checkout_request_id=checkout_request_id)
            order = payment.order

            # Prevent changing status if already paid
            if order.status == 'paid':
                logger.warning(f"[SIMULATION] Order {order.id} is already paid. Ignoring callback.")
                return Response({'ResultCode': 0, 'ResultDesc': 'Order already paid'}, status=200)

            # If previous payment attempt for this order failed, don't set to paid
            if Payment.objects.filter(order=order, status='failed').exists() and result_code == 0:
                logger.warning(f"[SIMULATION] Order {order.id} had a failed payment, keeping status pending.")
                payment.status = 'failed'
                payment.save()
                return Response({'ResultCode': 0, 'ResultDesc': 'Payment attempt ignored due to previous failure'}, status=200)

            if result_code == 0:  # Success
                mpesa_receipt = next(
                    (item['Value'] for item in stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    if item['Name'] == 'MpesaReceiptNumber'),
                    None
                )
                payment.mpesa_receipt_number = mpesa_receipt

                if payment.amount >= order.total_amount:
                    if payment.amount > order.total_amount:
                        payment.wallet = payment.amount - order.total_amount
                    payment.status = 'completed'
                    # Update order status on success
                    order.status = 'paid'
            else:
                payment.status = 'failed'
                # Update order status on failure (set to 'cancelled'; adjust if preferred)
                order.status = 'cancelled'

            payment.save()
            order.save()  # This will propagate to OrderItems via Order.save()
            logger.info(f"[SIMULATION] Payment {payment.id} updated to {payment.status}. Order {order.id} updated to {order.status}.")
            return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        except Payment.DoesNotExist:
            logger.error(f"[SIMULATION] No payment found for CheckoutRequestID: {checkout_request_id}")
            return Response({'ResultCode': 1, 'ResultDesc': 'Payment not found'}, status=404)