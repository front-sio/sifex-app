import logging
from copy import deepcopy
from typing import Any, Dict, Optional

from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from tcra_integration.metrics import increment
from tcra_integration.models import AuditLog, TcraEndpointConfig, TcraSubmission
from tcra_integration.services.client import TcraClient, TcraClientError, TcraClientRetryableError
from tcra_integration.services.validators import validate_submission_payload

logger = logging.getLogger(__name__)


class TcraSubmissionService:
    @staticmethod
    def _payload_with_operator_code(submission_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if submission_type not in {
            "SHIPMENT_CREATED",
            "SHIPMENT_UPDATED",
            "DELIVERY_CONFIRMED",
            "MANIFEST",
            "BILLING",
            "OTHER",
        }:
            return payload

        events = payload.get("eventsList")
        if not isinstance(events, list):
            return payload

        operator_code = getattr(settings, "TCRA_OPERATOR_CODE", None)
        if operator_code is None:
            return payload

        enriched_payload = deepcopy(payload)
        enriched_events = enriched_payload.get("eventsList", [])
        updated = False
        for event in enriched_events:
            if not isinstance(event, dict):
                continue
            msg_info = event.get("msgInfo")
            if not isinstance(msg_info, dict):
                msg_info = {}
                event["msgInfo"] = msg_info
            if msg_info.get("operatorCode") in (None, ""):
                msg_info["operatorCode"] = operator_code
                updated = True
        return enriched_payload if updated else payload

    @staticmethod
    def create_submission(
        submission_type: str, provider_reference: str, payload: Dict[str, Any], actor=None
    ) -> TcraSubmission:
        submission = TcraSubmission.objects.create(
            submission_type=submission_type,
            provider_reference=provider_reference,
            payload=payload,
        )
        AuditLog.objects.create(
            actor=actor,
            action="submission_created",
            object_type="TcraSubmission",
            object_id=str(submission.id),
            metadata={"submission_type": submission_type, "provider_reference": provider_reference},
        )
        return submission

    @staticmethod
    def enqueue_submission(submission_id: str) -> None:
        from tcra_integration.tasks import send_tcra_submission

        send_tcra_submission.delay(str(submission_id))

    @staticmethod
    def send_submission(submission_id: str) -> Dict[str, Any]:
        submission = TcraSubmission.objects.get(id=submission_id)
        config = TcraEndpointConfig.objects.filter(is_active=True).order_by("-updated_at").first()
        if not config:
            submission.status = TcraSubmission.Status.FAILED
            submission.last_error = "No active TCRA endpoint configuration"
            submission.last_attempt_at = timezone.now()
            submission.attempt_count += 1
            submission.save(update_fields=["status", "last_error", "last_attempt_at", "attempt_count"])
            return {"success": False, "retryable": False}

        path_map = getattr(settings, "TCRA_PATHS", {})
        path = path_map.get(submission.submission_type, path_map.get("DEFAULT", "/"))
        payload = TcraSubmissionService._payload_with_operator_code(submission.submission_type, submission.payload)
        payload_updated = payload is not submission.payload

        submission.attempt_count += 1
        submission.last_attempt_at = timezone.now()

        try:
            client = TcraClient(config=config)
        except TcraClientError as exc:
            submission.status = TcraSubmission.Status.FAILED
            submission.last_error = str(exc)
            submission.save(update_fields=["status", "last_error", "last_attempt_at", "attempt_count"])
            increment("tcra_submission_failed", submission_type=submission.submission_type)
            return {"success": False, "retryable": False}

        try:
            validate_submission_payload(submission.submission_type, payload)
        except ValidationError as exc:
            submission.status = TcraSubmission.Status.FAILED
            submission.last_error = f"Payload validation failed: {exc}"
            submission.save(update_fields=["status", "last_error", "last_attempt_at", "attempt_count"])
            increment("tcra_submission_failed", submission_type=submission.submission_type)
            return {"success": False, "retryable": False}

        with transaction.atomic():
            try:
                response = client.post_json(path, payload)
            except TcraClientRetryableError as exc:
                submission.status = TcraSubmission.Status.FAILED
                submission.last_error = str(exc)
                submission.save(update_fields=["status", "last_error", "last_attempt_at", "attempt_count"])
                increment("tcra_submission_failed", submission_type=submission.submission_type)
                return {"success": False, "retryable": True}
            except TcraClientError as exc:
                submission.status = TcraSubmission.Status.FAILED
                submission.last_error = str(exc)
                submission.save(update_fields=["status", "last_error", "last_attempt_at", "attempt_count"])
                increment("tcra_submission_failed", submission_type=submission.submission_type)
                return {"success": False, "retryable": False}

            submission.tcra_response_code = response.status_code
            submission.tcra_response_body = response.body_text
            if payload_updated:
                submission.payload = payload
            if 200 <= response.status_code < 300:
                submission.status = TcraSubmission.Status.SENT
                submission.sent_at = timezone.now()
                submission.last_error = None
                increment("tcra_submission_sent", submission_type=submission.submission_type)
            else:
                submission.status = TcraSubmission.Status.FAILED
                submission.last_error = f"Non-success response: {response.status_code} - {response.body_text[:500]}"
                increment("tcra_submission_failed", submission_type=submission.submission_type)
            submission.save(
                update_fields=[
                    "payload",
                    "status",
                    "last_error",
                    "last_attempt_at",
                    "attempt_count",
                    "tcra_response_code",
                    "tcra_response_body",
                    "sent_at",
                ]
            )

        retryable = response.status_code >= 500
        return {"success": submission.status == TcraSubmission.Status.SENT, "retryable": retryable}

    @staticmethod
    def last_successful_submission_at() -> Optional[timezone.datetime]:
        last_sent = (
            TcraSubmission.objects.filter(status=TcraSubmission.Status.SENT, sent_at__isnull=False)
            .order_by("-sent_at")
            .values_list("sent_at", flat=True)
            .first()
        )
        return last_sent
