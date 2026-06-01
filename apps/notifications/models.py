from django.db import models


class SMSTemplate(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SMSLog(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        SENT = "SENT", "Sent"
        DELIVERED = "DELIVERED", "Delivered"
        FAILED = "FAILED", "Failed"

    recipient = models.CharField(max_length=30)
    message_body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    provider = models.CharField(max_length=80, default="Internal Simulator")
    reference_id = models.CharField(max_length=80, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.status}"
