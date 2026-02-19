import logging
from typing import List

from celery import shared_task
from celery.exceptions import Retry
from django.conf import settings
from django.utils import timezone

from tcra_integration.models import AuditLog, TcraWebhookEvent
from tcra_integration.services.submissions import TcraSubmissionService

logger = logging.getLogger(__name__)


def _retry_backoffs() -> List[int]:
    return getattr(settings, "TCRA_RETRY_BACKOFFS", [60, 300, 900, 3600])


@shared_task(bind=True, autoretry_for=(), max_retries=getattr(settings, "TCRA_MAX_ATTEMPTS", 4))
def send_tcra_submission(self, submission_id: str) -> None:
    result = TcraSubmissionService.send_submission(submission_id)
    if result.get("success"):
        return

    if result.get("retryable"):
        backoffs = _retry_backoffs()
        attempt = self.request.retries
        countdown = backoffs[min(attempt, len(backoffs) - 1)]
        logger.warning(
            "Retrying TCRA submission",
            extra={"submission_id": submission_id, "retry_in": countdown, "attempt": attempt + 1},
        )
        raise self.retry(countdown=countdown)


@shared_task(bind=True, autoretry_for=(), max_retries=0)
def process_tcra_webhook_event(self, webhook_event_id: str) -> None:
    event = TcraWebhookEvent.objects.get(id=webhook_event_id)
    if event.processed:
        return
    if not event.signature_valid:
        event.processed = False
        event.processing_error = "Invalid signature"
        event.save(update_fields=["processed", "processing_error"])
        logger.warning(
            "Skipped TCRA webhook processing due to invalid signature",
            extra={"event_id": webhook_event_id},
        )
        return

    try:
        # TODO: Map inbound webhook body to internal models once TCRA spec is provided.
        event.processed = True
        event.processed_at = timezone.now()
        event.processing_error = None
        event.save(update_fields=["processed", "processed_at", "processing_error"])
        AuditLog.objects.create(
            actor=None,
            action="webhook_processed",
            object_type="TcraWebhookEvent",
            object_id=str(event.id),
            metadata={"signature_valid": event.signature_valid},
        )
    except Exception as exc:
        logger.exception("Failed processing TCRA webhook event", extra={"event_id": webhook_event_id})
        event.processed = False
        event.processing_error = str(exc)
        event.save(update_fields=["processed", "processing_error"])
