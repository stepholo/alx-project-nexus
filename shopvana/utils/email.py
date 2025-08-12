from utils.tasks import send_email_async


def send_notification_email(to_email, subject, template_name, context):
    # Offload the email sending task to Celery
    send_email_async.delay(subject, template_name, context, [to_email])
