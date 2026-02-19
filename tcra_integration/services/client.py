import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict

import requests
from django.conf import settings

from tcra_integration.metrics import observe
from tcra_integration.models import TcraEndpointConfig
from tcra_integration.services.crypto import TcraCryptoError, sign_request_body, signature_header_name

logger = logging.getLogger(__name__)


class TcraClientError(Exception):
    pass


class TcraClientRetryableError(TcraClientError):
    pass


@dataclass
class TcraResponse:
    status_code: int
    body_text: str
    elapsed_seconds: float


class TcraClient:
    def __init__(self, config: TcraEndpointConfig) -> None:
        self.config = config

    def post_json(self, path: str, payload: Dict[str, Any]) -> TcraResponse:
        url = self._build_url(path)
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        headers = self._build_headers(body)
        redacted_headers = self._redact_headers(headers)
        timeout_seconds = self.config.timeout_seconds

        logger.info(
            "TCRA outbound request",
            extra={
                "tcra_url": url,
                "tcra_headers": redacted_headers,
                "tcra_timeout": timeout_seconds,
            },
        )
        started = time.monotonic()
        try:
            response = requests.post(
                url,
                headers=headers,
                data=body,
                timeout=timeout_seconds,
                verify=self.config.verify_ssl,
            )
        except requests.RequestException as exc:
            observe("tcra_request_latency_seconds", time.monotonic() - started, outcome="exception")
            logger.exception("TCRA outbound request failed", extra={"tcra_url": url})
            raise TcraClientRetryableError(str(exc)) from exc

        elapsed = time.monotonic() - started
        observe("tcra_request_latency_seconds", elapsed, outcome=str(response.status_code))
        logger.info(
            "TCRA outbound response",
            extra={
                "tcra_url": url,
                "tcra_status": response.status_code,
                "tcra_response": self._truncate(response.text),
            },
        )
        return TcraResponse(status_code=response.status_code, body_text=response.text, elapsed_seconds=elapsed)

    def _build_url(self, path: str) -> str:
        base = self.config.base_url or getattr(settings, "TCRA_BASE_URL", "")
        if not base:
            raise TcraClientError("TCRA base URL is not configured")
        return f"{base.rstrip('/')}/{path.lstrip('/')}"

    def _build_headers(self, body: str) -> Dict[str, str]:
        try:
            header_name = signature_header_name()
            signature = sign_request_body(body.encode("utf-8"))
        except TcraCryptoError as exc:
            raise TcraClientError(str(exc)) from exc

        return {
            "Content-Type": "application/json",
            header_name: signature,
        }

    def _redact_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        redacted = {}
        secret_headers = {"authorization", "x-api-key", signature_header_name().lower()}
        for key, value in headers.items():
            if key.lower() in secret_headers:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = value
        return redacted

    def _truncate(self, value: str, limit: int = 2000) -> str:
        if value is None:
            return ""
        if len(value) <= limit:
            return value
        return value[:limit] + "..."
