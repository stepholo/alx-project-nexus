from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from celery import shared_task
from payments.views import PaymentViewSet


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
        html_message=html_message,
        fail_silently=False,
    )


@shared_task
def simulate_payment_status_update(checkout_request_id):
    PaymentViewSet().simulate_callback(checkout_request_id)
