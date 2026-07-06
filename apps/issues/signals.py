from django.apps import apps
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Issue


@receiver(pre_save, sender=Issue)
def stash_previous_state(sender, instance, **kwargs):
    if instance.pk:
        previous = Issue.objects.filter(pk=instance.pk).values(
            "status", "assigned_technician_name", "appointment_at"
        ).first()
    else:
        previous = None
    instance._previous_state = previous


@receiver(post_save, sender=Issue)
def log_issue_save(sender, instance, created, **kwargs):
    try:
        AuditLog = apps.get_model("reports", "AuditLog")
    except LookupError:
        return

    AuditLog.objects.create(
        actor=instance.assigned_officer,
        action="created" if created else "updated",
        entity_type="Issue",
        entity_id=str(instance.pk),
        summary=instance.title,
        metadata={"status": instance.status, "reference_no": instance.reference_no},
    )


@receiver(post_save, sender=Issue)
def notify_issue_progress(sender, instance, created, **kwargs):
    if created or not instance.citizen.user_id:
        return
    previous = getattr(instance, "_previous_state", None)
    if not previous:
        return
    try:
        Notification = apps.get_model("notifications", "Notification")
    except LookupError:
        return

    appointment_newly_set = (
        instance.assigned_technician_name and instance.appointment_at
        and (instance.assigned_technician_name != previous["assigned_technician_name"]
             or instance.appointment_at != previous["appointment_at"])
    )
    if appointment_newly_set:
        Notification.objects.create(
            recipient_id=instance.citizen.user_id,
            message=(
                f"Technician {instance.assigned_technician_name} scheduled to visit for "
                f"{instance.reference_no} on {instance.appointment_at.strftime('%d %b %Y, %H:%M')}."
            ),
            related_issue=instance,
        )

    if instance.status == Issue.Status.RESOLVED and previous["status"] != Issue.Status.RESOLVED:
        Notification.objects.create(
            recipient_id=instance.citizen.user_id,
            message=f"Your request {instance.reference_no} has been resolved. Please rate the service.",
            related_issue=instance,
        )
