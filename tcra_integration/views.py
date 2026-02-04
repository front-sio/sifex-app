import hashlib
import hmac
import json
import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tcra_integration.models import TcraEndpointConfig, TcraSubmission, TcraWebhookEvent
from tcra_integration.serializers import (
    TcraHealthSerializer,
    TcraSubmissionCreateSerializer,
    TcraSubmissionRetrySerializer,
    TcraSubmissionSerializer,
)
from tcra_integration.services.submissions import TcraSubmissionService
from tcra_integration.tasks import process_tcra_webhook_event

logger = logging.getLogger(__name__)


def _parse_body(raw_body: bytes) -> Any:
    if not raw_body:
        return None
    try:
        return json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        return raw_body.decode("utf-8", errors="replace")


def _signature_is_valid(raw_body: bytes, provided_signature: Optional[str]) -> bool:
    secret = getattr(settings, "TCRA_WEBHOOK_SECRET", None)
    if not secret:
        return False
    if not provided_signature:
        return False
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, provided_signature)


class TcraSubmissionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAdminUser]
    queryset = TcraSubmission.objects.all().order_by("-created_at")
    serializer_class = TcraSubmissionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = request.query_params.get("status")
        type_filter = request.query_params.get("type")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if type_filter:
            queryset = queryset.filter(submission_type=type_filter)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        submission = self.get_object()
        serializer = self.get_serializer(submission)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = TcraSubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = TcraSubmissionService.create_submission(
            submission_type=serializer.validated_data["submission_type"],
            provider_reference=serializer.validated_data["provider_reference"],
            payload=serializer.validated_data["payload"],
            actor=request.user,
        )
        TcraSubmissionService.enqueue_submission(submission.id)
        output = TcraSubmissionSerializer(submission)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        submission = self.get_object()
        serializer = TcraSubmissionRetrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        TcraSubmissionService.enqueue_submission(submission.id)
        return Response({"queued": True})


class TcraHealthView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        config = TcraEndpointConfig.objects.filter(is_active=True).order_by("-updated_at").first()
        last_success = TcraSubmissionService.last_successful_submission_at()
        data = {
            "active_config": bool(config),
            "base_url": config.base_url if config else "",
            "auth_type": config.auth_type if config else "",
            "last_successful_send": last_success,
        }
        serializer = TcraHealthSerializer(data)
        return Response(serializer.data)


class TcraWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        raw_body = request.body
        body = _parse_body(raw_body)
        signature_header = getattr(settings, "TCRA_WEBHOOK_SIGNATURE_HEADER", "X-TCRA-Signature")
        signature = request.headers.get(signature_header)
        signature_valid = _signature_is_valid(raw_body, signature)

        event = TcraWebhookEvent.objects.create(
            headers=dict(request.headers),
            body=body,
            signature_valid=signature_valid,
        )
        logger.info(
            "TCRA webhook received",
            extra={"event_id": str(event.id), "signature_valid": signature_valid},
        )

        process_tcra_webhook_event.delay(str(event.id))
        return Response({"received": True}, status=status.HTTP_200_OK)
