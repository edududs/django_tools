from django.db import models


class Status(models.TextChoices):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class OutBox(models.Model):
    message = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)

    def __str__(self):
        return f"OutBox {self.pk}"


class InBox(models.Model):
    message = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)

    def __str__(self):
        return f"InBox {self.pk}"
