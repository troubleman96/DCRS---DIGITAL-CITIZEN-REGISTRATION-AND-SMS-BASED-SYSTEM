from django.apps import apps
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.notifications.services import send_sms

from .models import Citizen


@receiver(pre_save, sender=Citizen)
def stash_previous_status(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_status = Citizen.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    else:
        instance._previous_status = None


@receiver(post_save, sender=Citizen)
def log_citizen_save(sender, instance, created, **kwargs):
    try:
        AuditLog = apps.get_model("reports", "AuditLog")
    except LookupError:
        return

    AuditLog.objects.create(
        actor=instance.user,
        action="created" if created else "updated",
        entity_type="Citizen",
        entity_id=str(instance.pk),
        summary=instance.full_name,
        metadata={"status": instance.status, "citizen_id": instance.citizen_id},
    )


@receiver(post_save, sender=Citizen)
def notify_citizen_status_change(sender, instance, created, **kwargs):
    if created or not instance.user_id:
        return
    previous_status = getattr(instance, "_previous_status", None)
    if previous_status == instance.status:
        return
    try:
        Notification = apps.get_model("notifications", "Notification")
    except LookupError:
        return

    if instance.status == Citizen.Status.APPROVED:
        message = f"Your DCRS registration ({instance.citizen_id}) has been approved."
    elif instance.status == Citizen.Status.REJECTED:
        message = f"Your DCRS registration ({instance.citizen_id}) was rejected: {instance.rejection_reason}"
    else:
        return

    Notification.objects.create(recipient_id=instance.user_id, message=message)


@receiver(post_save, sender=Citizen)
def notify_officers_of_new_registration(sender, instance, created, **kwargs):
    """Alert the ward's officers (and all admins) when a new citizen registers, so approvals
    don't sit unnoticed."""
    if not created:
        return
    try:
        Notification = apps.get_model("notifications", "Notification")
    except LookupError:
        return

    User = apps.get_model("accounts", "User")
    recipients = User.objects.filter(
        models.Q(role=User.Role.ADMIN) | models.Q(role=User.Role.OFFICER, ward=instance.ward)
    ).distinct()

    message = f"New citizen registration: {instance.full_name} ({instance.citizen_id}) in {instance.ward.name} — awaiting approval."
    Notification.objects.bulk_create(
        [Notification(recipient=user, message=message, related_citizen=instance) for user in recipients]
    )

    # SMS the ward's officer(s) directly — admins get the web notification only, to avoid
    # mass-SMS-ing every admin account on every single registration.
    for officer in recipients.filter(role=User.Role.OFFICER):
        if officer.phone_number:
            send_sms(
                officer.phone_number,
                f"DCRS: New citizen registration awaiting your approval — {instance.full_name} "
                f"({instance.citizen_id}) in {instance.ward.name}.",
            )
