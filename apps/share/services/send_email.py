from decouple import config
from django.core.mail import send_mail

from apps.share.services.tenant_error_logger import TenantLogger


def email_send(request, subject, message, recipient_list):
    try:
        send_mail(
            subject,
            message,
            config("DEFAULT_FROM_EMAIL"),
            recipient_list,
            fail_silently=False,
        )
    except Exception as e:
        tenant_logger = TenantLogger(request)
        tenant_logger.error(e)