import base64
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from tcra_integration.models import TcraWebhookEvent


def _generate_test_certificate():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "tcra-webhook-test")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(minutes=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=30))
        .sign(private_key, hashes.SHA256())
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    return private_key_pem, base64.b64encode(cert_pem).decode("ascii")


class TcraWebhookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.private_key_pem, cls.cert_b64 = _generate_test_certificate()

    def setUp(self):
        self.client = APIClient()

    @override_settings(
        TCRA_SIGNATURE_HEADER="X-TCRA-Signature",
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_BROKER_URL="memory://",
        CELERY_RESULT_BACKEND="cache+memory://",
    )
    def test_webhook_signature_valid(self):
        payload = {"event": "delivered"}
        raw_body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        private_key = serialization.load_pem_private_key(self.private_key_pem, password=None)
        signature = base64.b64encode(
            private_key.sign(raw_body, padding.PKCS1v15(), hashes.SHA256())
        ).decode("ascii")

        with override_settings(TCRA_WEBHOOK_PUBLIC_CERT_B64=self.cert_b64):
            with patch("tcra_integration.views.process_tcra_webhook_event.delay") as mocked_delay:
                response = self.client.post(
                    "/webhooks/tcra/",
                    data=raw_body,
                    content_type="application/json",
                    HTTP_X_TCRA_SIGNATURE=signature,
                )

        self.assertEqual(response.status_code, 200)
        mocked_delay.assert_called_once()
        event = TcraWebhookEvent.objects.first()
        self.assertTrue(event.signature_valid)
        self.assertEqual(event.body, payload)

    @override_settings(
        TCRA_SIGNATURE_HEADER="X-TCRA-Signature",
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_BROKER_URL="memory://",
        CELERY_RESULT_BACKEND="cache+memory://",
    )
    def test_webhook_signature_invalid_returns_401_and_not_queued(self):
        payload = {"event": "failed"}
        raw_body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

        with override_settings(TCRA_WEBHOOK_PUBLIC_CERT_B64=self.cert_b64):
            with patch("tcra_integration.views.process_tcra_webhook_event.delay") as mocked_delay:
                response = self.client.post(
                    "/webhooks/tcra/",
                    data=raw_body,
                    content_type="application/json",
                    HTTP_X_TCRA_SIGNATURE="invalid",
                )

        self.assertEqual(response.status_code, 401)
        mocked_delay.assert_not_called()
        event = TcraWebhookEvent.objects.first()
        self.assertFalse(event.signature_valid)

    @override_settings(
        TCRA_SIGNATURE_HEADER="X-TCRA-Signature",
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_BROKER_URL="memory://",
        CELERY_RESULT_BACKEND="cache+memory://",
    )
    def test_webhook_missing_signature_returns_401(self):
        payload = {"event": "missing-signature"}
        raw_body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

        with override_settings(TCRA_WEBHOOK_PUBLIC_CERT_B64=self.cert_b64):
            with patch("tcra_integration.views.process_tcra_webhook_event.delay") as mocked_delay:
                response = self.client.post(
                    "/webhooks/tcra/",
                    data=raw_body,
                    content_type="application/json",
                )

        self.assertEqual(response.status_code, 401)
        mocked_delay.assert_not_called()
