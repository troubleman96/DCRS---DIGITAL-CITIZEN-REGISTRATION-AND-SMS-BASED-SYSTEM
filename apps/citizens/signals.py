from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Citizen


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
