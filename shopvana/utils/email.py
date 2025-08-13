from utils.tasks import send_email_async
import logging


def send_notification_email(to_email, subject, template_name, context):
    # Offload the email sending task to Celery
    logging.info(f"Sending email to {to_email} with subject: {subject}")
    send_email_async.delay(subject, template_name, context, [to_email])
