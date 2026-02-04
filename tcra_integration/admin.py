from django.contrib import admin
from .models import AuditLog, TcraEndpointConfig, TcraSubmission, TcraWebhookEvent


@admin.register(TcraEndpointConfig)
class TcraEndpointConfigAdmin(admin.ModelAdmin):
    list_display = ("base_url", "auth_type", "is_active", "timeout_seconds", "verify_ssl", "updated_at")
    list_filter = ("auth_type", "is_active", "verify_ssl")
    search_fields = ("base_url",)


@admin.register(TcraSubmission)
class TcraSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission_type",
        "provider_reference",
        "status",
        "attempt_count",
        "last_attempt_at",
        "sent_at",
        "created_at",
    )
    list_filter = ("status", "submission_type")
    search_fields = ("provider_reference", "id")
    readonly_fields = (
        "tcra_response_body",
        "tcra_response_code",
        "last_error",
        "attempt_count",
        "last_attempt_at",
        "sent_at",
        "created_at",
    )


@admin.register(TcraWebhookEvent)
class TcraWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("id", "received_at", "signature_valid", "processed", "processed_at")
    list_filter = ("signature_valid", "processed")
    readonly_fields = ("headers", "body", "received_at", "processed_at", "processing_error")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "object_type", "object_id", "actor", "created_at")
    search_fields = ("object_type", "object_id", "action")
    readonly_fields = ("created_at",)
