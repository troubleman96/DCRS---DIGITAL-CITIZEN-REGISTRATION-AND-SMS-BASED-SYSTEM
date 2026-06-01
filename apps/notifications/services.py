from django.utils import timezone

from .models import SMSLog


def send_sms(recipient, message_body, provider="Internal Simulator", reference_id=""):
    return SMSLog.objects.create(
        recipient=recipient,
        message_body=message_body,
        status=SMSLog.Status.SENT,
        provider=provider,
        reference_id=reference_id,
        sent_at=timezone.now(),
    )


def broadcast_sms(recipients, message_body, provider="Internal Simulator"):
    return [send_sms(recipient, message_body, provider=provider) for recipient in recipients]
