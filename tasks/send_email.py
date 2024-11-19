from django.core.mail import send_mail
from celery import shared_task

from navyojan import settings
from tasks import decrypt_data
from logs import logger


@shared_task(name='send_email_task')
def send_email_task(subject, body, to_user_emails):
    logger.info(f"Sending email with subject: {subject}, body: {body}, to: {to_user_emails}")
    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            to_user_emails,
            fail_silently=False,
        )
        logger.info(f"email sent to: {to_user_emails}")
    except Exception as e:
        logger.debug(f"Error: {e}")
