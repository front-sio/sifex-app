from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from tcra_integration.models import TcraEndpointConfig, TcraSubmission
from tcra_integration.services.submissions import TcraSubmissionService


class TcraSubmissionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="password",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(self.user)

    @patch("tcra_integration.services.submissions.TcraSubmissionService.enqueue_submission")
    def test_create_submission(self, mocked_enqueue):
        payload = {"tracking_number": "ABC123"}
        response = self.client.post(
            "/api/tcra/submissions/",
            {
                "submission_type": "SHIPMENT_CREATED",
                "provider_reference": "ref-1",
                "payload": payload,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], TcraSubmission.Status.PENDING)
        mocked_enqueue.assert_called_once()

    def test_list_filters(self):
        submission_one = TcraSubmissionService.create_submission(
            submission_type="SHIPMENT_CREATED",
            provider_reference="ref-1",
            payload={"a": 1},
            actor=self.user,
        )
        submission_two = TcraSubmissionService.create_submission(
            submission_type="DELIVERY_CONFIRMED",
            provider_reference="ref-2",
            payload={"b": 2},
            actor=self.user,
        )
        submission_two.status = TcraSubmission.Status.FAILED
        submission_two.save(update_fields=["status"])

        response = self.client.get("/api/tcra/submissions/?status=FAILED")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(submission_two.id))

    @patch("tcra_integration.services.submissions.TcraSubmissionService.enqueue_submission")
    def test_retry_submission(self, mocked_enqueue):
        submission = TcraSubmissionService.create_submission(
            submission_type="SHIPMENT_CREATED",
            provider_reference="ref-3",
            payload={"a": 1},
            actor=self.user,
        )
        response = self.client.post(f"/api/tcra/submissions/{submission.id}/retry/", {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["queued"])
        mocked_enqueue.assert_called_once()

    def test_health(self):
        TcraEndpointConfig.objects.create(
            base_url="https://example.com",
            auth_type=TcraEndpointConfig.AuthType.API_KEY,
            api_key="key",
        )
        submission = TcraSubmissionService.create_submission(
            submission_type="SHIPMENT_CREATED",
            provider_reference="ref-4",
            payload={"a": 1},
            actor=self.user,
        )
        submission.status = TcraSubmission.Status.SENT
        submission.sent_at = submission.created_at
        submission.save(update_fields=["status", "sent_at"])

        response = self.client.get("/api/tcra/health/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["active_config"])
        self.assertIsNotNone(response.data["last_successful_send"])
