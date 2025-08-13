import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

CHAPA_VERIFY_URL = f"{settings.CHAPA_BASE_URL.rstrip('/')}/transaction/verify/"
CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY


def verify_chapa_payment(payment):
    """
    Verify a payment with Chapa and update status/order accordingly.
    Returns (status, receipt_url) tuple.
    """
    headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
    chapa_resp = requests.get(f"{CHAPA_VERIFY_URL}{payment.chapa_tx_ref}", headers=headers)

    if chapa_resp.status_code != 200:
        return "error", None

    resp_data = chapa_resp.json()
    status_str = resp_data.get('data', {}).get('status')
    receipt_url = resp_data.get('data', {}).get('receipt_url')

    if status_str == "success":
        payment.status = "completed"
        payment.order.status = "paid"
        payment.order.save()
        payment.save()

        # Send receipt email
        from utils.email import send_notification_email
        send_notification_email(
            to_email=payment.user.email,
            subject="Your Payment Receipt",
            template_name="emails/payment_receipt.html",
            context={
                "user_name": payment.user.get_full_name() or payment.user.username,
                "order_id": payment.order.id,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.payment_method,
                "transaction_id": payment.chapa_tx_ref,
                "paid_at": payment.updated_at,
                "chapa_receipt_url": receipt_url
            }
        )

    elif status_str == "failed":
        payment.status = "failed"
        payment.order.status = "cancelled"
        payment.order.save()
        payment.save()

    return status_str, receipt_url
