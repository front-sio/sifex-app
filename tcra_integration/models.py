import uuid
from django.conf import settings
from django.db import models


class TcraEndpointConfig(models.Model):
    class AuthType(models.TextChoices):
        API_KEY = "API_KEY", "API Key"
        BASIC = "BASIC", "Basic"
        OAUTH2 = "OAUTH2", "OAuth2"

    base_url = models.URLField()
    auth_type = models.CharField(max_length=20, choices=AuthType.choices, default=AuthType.API_KEY)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    token_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    timeout_seconds = models.PositiveIntegerField(default=30)
    verify_ssl = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"TCRA Endpoint ({self.base_url})"


class TcraSubmission(models.Model):
    class SubmissionType(models.TextChoices):
        SHIPMENT_CREATED = "SHIPMENT_CREATED", "Shipment Created"
        SHIPMENT_UPDATED = "SHIPMENT_UPDATED", "Shipment Updated"
        DELIVERY_CONFIRMED = "DELIVERY_CONFIRMED", "Delivery Confirmed"
        MANIFEST = "MANIFEST", "Manifest"
        BILLING = "BILLING", "Billing"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_type = models.CharField(max_length=50, choices=SubmissionType.choices)
    provider_reference = models.CharField(max_length=255)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    attempt_count = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    tcra_response_code = models.PositiveIntegerField(blank=True, null=True)
    tcra_response_body = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.submission_type} ({self.id})"


class TcraWebhookEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    received_at = models.DateTimeField(auto_now_add=True)
    headers = models.JSONField()
    body = models.JSONField(blank=True, null=True)
    signature_valid = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)
    processing_error = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Webhook Event ({self.id})"


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tcra_audit_logs",
    )
    action = models.CharField(max_length=255)
    object_type = models.CharField(max_length=255)
    object_id = models.CharField(max_length=255)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.action} {self.object_type} {self.object_id}"
