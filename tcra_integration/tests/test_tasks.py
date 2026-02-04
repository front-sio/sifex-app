from unittest.mock import patch

from celery.exceptions import Retry
from django.test import TestCase, override_settings

from tcra_integration.tasks import send_tcra_submission


class TcraTaskRetryTests(TestCase):
    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_BROKER_URL="memory://",
        CELERY_RESULT_BACKEND="cache+memory://",
    )
    def test_send_submission_retries_on_retryable(self):
        with patch("tcra_integration.services.submissions.TcraSubmissionService.send_submission") as mocked:
            mocked.return_value = {"success": False, "retryable": True}
            with self.assertRaises(Retry):
                send_tcra_submission.delay("00000000-0000-0000-0000-000000000000")

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_BROKER_URL="memory://",
        CELERY_RESULT_BACKEND="cache+memory://",
    )
    def test_send_submission_no_retry_on_non_retryable(self):
        with patch("tcra_integration.services.submissions.TcraSubmissionService.send_submission") as mocked:
            mocked.return_value = {"success": False, "retryable": False}
            result = send_tcra_submission.delay("00000000-0000-0000-0000-000000000000")
            self.assertTrue(result.successful())
