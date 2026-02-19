from typing import Any, Dict

from django.core.exceptions import ValidationError
from jsonschema import Draft7Validator

from tcra_integration.schemas import SCHEMAS


def _schema_key_for_submission(submission_type: str) -> str:
    # Legacy submission types map to the events endpoint by default.
    events_types = {
        "SHIPMENT_CREATED",
        "SHIPMENT_UPDATED",
        "DELIVERY_CONFIRMED",
        "MANIFEST",
        "BILLING",
        "OTHER",
        "EVENTS",
    }
    if submission_type in events_types:
        return "events"
    if submission_type == "SNAPSHOT":
        return "snapshot"
    if submission_type == "CALLBACK":
        return "callback"
    return "events"


def validate_submission_payload(submission_type: str, payload: Dict[str, Any]) -> None:
    schema_key = _schema_key_for_submission(submission_type)
    validator = Draft7Validator(SCHEMAS[schema_key])
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
    if errors:
        messages = [f"{'/'.join(map(str, err.path))}: {err.message}" for err in errors]
        raise ValidationError("; ".join(messages))
