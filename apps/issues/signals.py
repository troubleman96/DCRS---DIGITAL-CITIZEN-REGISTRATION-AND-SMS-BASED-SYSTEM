from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Issue


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
