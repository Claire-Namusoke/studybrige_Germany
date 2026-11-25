import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send_email(*, subject, body, recipient, reference, notification_type):
    try:
        sent_count = send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except (OSError, SMTPException):
        logger.exception(
            "Could not send %s email for request %s.",
            notification_type,
            reference,
        )
        return False

    if sent_count != 1:
        logger.error(
            "Email backend did not send %s email for request %s.",
            notification_type,
            reference,
        )
        return False
    return True


def send_submission_notifications(submission, *, request_type):
    reference = str(submission.reference)
    if request_type == "consultation":
        next_steps = (
            "Our team will check availability and contact you. Your requested date "
            "and time are preferences, not a confirmed appointment."
        )
    else:
        next_steps = "Our team will review your enquiry and contact you."
    confirmation_body = (
        f"Hello {submission.full_name},\n\n"
        f"We have received your {request_type} request.\n"
        f"Reference: {reference}\n\n"
        f"{next_steps}\n\n"
        "StudyBridge Germany"
    )
    confirmation_sent = _send_email(
        subject=f"Your StudyBridge Germany {request_type} request",
        body=confirmation_body,
        recipient=submission.email,
        reference=reference,
        notification_type="customer confirmation",
    )

    if not settings.BUSINESS_NOTIFICATION_EMAIL:
        logger.warning(
            "BUSINESS_NOTIFICATION_EMAIL is not configured; request %s is available in Django Admin.",
            reference,
        )
        return confirmation_sent, False

    admin_body = (
        f"A new {request_type} request was submitted.\n"
        f"Reference: {reference}\n"
        "Open Django Admin to review the request."
    )
    admin_sent = _send_email(
        subject=f"New StudyBridge Germany {request_type} request",
        body=admin_body,
        recipient=settings.BUSINESS_NOTIFICATION_EMAIL,
        reference=reference,
        notification_type="business notification",
    )
    return confirmation_sent, admin_sent
