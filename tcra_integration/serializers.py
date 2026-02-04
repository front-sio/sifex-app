from typing import Any, Dict

from rest_framework import serializers

from tcra_integration.models import TcraSubmission


class TcraSubmissionCreateSerializer(serializers.Serializer):
    submission_type = serializers.ChoiceField(choices=TcraSubmission.SubmissionType.choices)
    provider_reference = serializers.CharField(max_length=255)
    payload = serializers.JSONField()


class TcraSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TcraSubmission
        fields = (
            "id",
            "submission_type",
            "provider_reference",
            "payload",
            "status",
            "attempt_count",
            "last_attempt_at",
            "last_error",
            "tcra_response_code",
            "tcra_response_body",
            "sent_at",
            "created_at",
        )
        read_only_fields = fields


class TcraSubmissionRetrySerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class TcraHealthSerializer(serializers.Serializer):
    active_config = serializers.BooleanField()
    base_url = serializers.CharField(allow_blank=True)
    auth_type = serializers.CharField(allow_blank=True)
    last_successful_send = serializers.DateTimeField(allow_null=True)

    def create(self, validated_data: Dict[str, Any]):
        return validated_data

    def update(self, instance, validated_data: Dict[str, Any]):
        return validated_data
