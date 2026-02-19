from typing import Any, Dict

# JSON Schemas for TCRA payloads.

EVENTS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "eventsList": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "msgInfo": {
                        "type": "object",
                        "properties": {
                            "msgId": {"type": "string"},
                            "operationCode": {"type": "string"},
                            "operatorCode": {"type": "number"},
                            "timestamp": {"type": "string", "format": "date-time"},
                        },
                        "required": ["msgId", "operationCode", "operatorCode", "timestamp"],
                    },
                    "txnInfo": {"type": "object"},
                },
                "required": ["msgInfo", "txnInfo"],
            },
        }
    },
}

# Placeholder schemas for snapshot and callback; replace with full spec when available.
SNAPSHOT_SCHEMA: Dict[str, Any] = {
    "type": "object",
}

CALLBACK_SCHEMA: Dict[str, Any] = {
    "type": "object",
}

SCHEMAS: Dict[str, Dict[str, Any]] = {
    "events": EVENTS_SCHEMA,
    "snapshot": SNAPSHOT_SCHEMA,
    "callback": CALLBACK_SCHEMA,
}
