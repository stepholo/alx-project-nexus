from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from payments.models import Payment
from payments.utils import verify_chapa_payment
import logging


logger = logging.getLogger(__name__)

CHAPA_VERIFY_URL = f"{settings.CHAPA_BASE_URL.rstrip('/')}/transaction/verify/"
CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY

@shared_task
def send_email_async(subject: str, template_name: str, context: dict, recipient_list: list) -> None:
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
def check_pending_payments() -> None:
    """Check and update the status of pending payments.
       Send payment receipt emails for completed payments.
    """
    pending_payments = Payment.objects.filter(status="pending")
    for payment in pending_payments:
        verify_chapa_payment(payment)
        logger.info(f"Checked payment {payment.chapa_tx_ref} status.")