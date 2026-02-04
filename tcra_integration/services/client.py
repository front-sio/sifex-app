import base64
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from django.conf import settings
from django.core.cache import cache

from tcra_integration.metrics import observe
from tcra_integration.models import TcraEndpointConfig

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

    def build_auth_headers(self) -> Dict[str, str]:
        if self.config.auth_type == TcraEndpointConfig.AuthType.API_KEY:
            header_name = getattr(settings, "TCRA_API_KEY_HEADER", "X-API-Key")
            if not self.config.api_key:
                logger.warning("TCRA API key auth selected but api_key is empty")
                return {}
            return {header_name: self.config.api_key}
        if self.config.auth_type == TcraEndpointConfig.AuthType.BASIC:
            if not self.config.username or not self.config.password:
                logger.warning("TCRA basic auth selected but username/password missing")
                return {}
            token = base64.b64encode(f"{self.config.username}:{self.config.password}".encode("utf-8")).decode(
                "ascii"
            )
            return {"Authorization": f"Basic {token}"}
        if self.config.auth_type == TcraEndpointConfig.AuthType.OAUTH2:
            token = self._get_oauth_token()
            if not token:
                return {}
            return {"Authorization": f"Bearer {token}"}
        return {}

    def post_json(self, path: str, payload: Dict[str, Any]) -> TcraResponse:
        url = self._build_url(path)
        headers = {"Content-Type": "application/json"}
        headers.update(self.build_auth_headers())
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
                data=json.dumps(payload),
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
        return f"{self.config.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _get_oauth_token(self) -> Optional[str]:
        cache_key = getattr(settings, "TCRA_OAUTH_TOKEN_CACHE_KEY", "tcra_oauth_token")
        cached = cache.get(cache_key)
        if cached:
            return cached

        if not (self.config.client_id and self.config.client_secret and self.config.token_url):
            logger.warning("TCRA OAuth2 configured but client credentials or token_url missing")
            return None

        # TODO: Replace with TCRA OAuth2 spec when provided (grant type, scopes, token response shape).
        try:
            response = requests.post(
                self.config.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                },
                timeout=self.config.timeout_seconds,
                verify=self.config.verify_ssl,
            )
            response.raise_for_status()
            token_payload = response.json()
            access_token = token_payload.get("access_token")
            expires_in = token_payload.get("expires_in", 3600)
            if access_token:
                cache.set(cache_key, access_token, timeout=int(expires_in) - 60)
            return access_token
        except requests.RequestException as exc:
            logger.exception("TCRA OAuth2 token request failed")
            raise TcraClientRetryableError(str(exc)) from exc

    def _redact_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        redacted = {}
        secret_headers = {"authorization", "x-api-key"}
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
