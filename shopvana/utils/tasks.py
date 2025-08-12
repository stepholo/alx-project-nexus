from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from payments.models import Payment
from django.conf import settings
import requests
import logging


logger = logging.getLogger(__name__)

CHAPA_VERIFY_URL = f"{settings.CHAPA_BASE_URL.rstrip('/')}/transaction/verify/"
CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY

@shared_task
def send_email_async(subject, template_name, context, recipient_list):
    """
    A Celery task to send an email using a template.

    :param subject: Subject of the email
    :param template_name: Name of the template to render the email body
    :param context: Context data to render the template
    :param recipient_list: List of email addresses to send the email to
    param html_message: Optional HTML message to send
    """
    message = render_to_string(template_name, context)
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=message,
        fail_silently=False,
    )

@shared_task
def check_pending_payments():
    pending_payments = Payment.objects.filter(status="pending")
    headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}

    for payment in pending_payments:
        tx_ref = payment.chapa_tx_ref
        try:
            chapa_resp = requests.get(f"{CHAPA_VERIFY_URL}{tx_ref}", headers=headers)
            if chapa_resp.status_code == 200:
                resp_data = chapa_resp.json()
                status_str = resp_data['data']['status']
                if status_str == "success":
                    payment.status = "completed"
                    payment.order.status = "paid"
                    payment.order.save()
                elif status_str == "failed":
                    payment.status = "failed"
                    payment.order.status = "cancelled"
                    payment.order.save()
                payment.save()
        except Exception as e:
            logger.error(f"Error checking payment {tx_ref}: {e}")
