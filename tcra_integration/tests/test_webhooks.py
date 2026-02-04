import hashlib
import hmac
import json

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from tcra_integration.models import TcraWebhookEvent


class TcraWebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(
        TCRA_WEBHOOK_SECRET="secret",
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_BROKER_URL="memory://",
        CELERY_RESULT_BACKEND="cache+memory://",
    )
    def test_webhook_signature_valid(self):
        payload = {"event": "delivered"}
        raw_body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(b"secret", raw_body, hashlib.sha256).hexdigest()

        response = self.client.post(
            "/webhooks/tcra/",
            data=raw_body,
            content_type="application/json",
            HTTP_X_TCRA_SIGNATURE=signature,
        )
        self.assertEqual(response.status_code, 200)
        event = TcraWebhookEvent.objects.first()
        self.assertTrue(event.signature_valid)
        self.assertEqual(event.body, payload)

    @override_settings(
        TCRA_WEBHOOK_SECRET="secret",
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_BROKER_URL="memory://",
        CELERY_RESULT_BACKEND="cache+memory://",
    )
    def test_webhook_signature_invalid(self):
        payload = {"event": "failed"}
        raw_body = json.dumps(payload).encode("utf-8")
        response = self.client.post(
            "/webhooks/tcra/",
            data=raw_body,
            content_type="application/json",
            HTTP_X_TCRA_SIGNATURE="invalid",
        )
        self.assertEqual(response.status_code, 200)
        event = TcraWebhookEvent.objects.first()
        self.assertFalse(event.signature_valid)
