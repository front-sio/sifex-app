import base64
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from django.test import TestCase, override_settings

from tcra_integration.models import TcraEndpointConfig
from tcra_integration.services.client import TcraClient, TcraClientError


def _build_pkcs12_material(password: str):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "tcra-test")])
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
    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=b"tcra",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8")),
    )
    return cert, pfx_bytes


class TcraClientSignatureTests(TestCase):
    def setUp(self):
        self.config = TcraEndpointConfig.objects.create(
            base_url="https://example.com",
            auth_type=TcraEndpointConfig.AuthType.API_KEY,
            api_key="unused",
        )

    def test_build_headers_uses_configured_signature_header(self):
        cert, pfx_bytes = _build_pkcs12_material("pfx-pass")
        body = json.dumps({"eventsList": []}, separators=(",", ":"), ensure_ascii=False)
        pfx_path = f"/tmp/tcra_private_test_client_{uuid.uuid4().hex}.pfx"
        with open(pfx_path, "wb") as pfx_file:
            pfx_file.write(pfx_bytes)

        try:
            with override_settings(
                TCRA_PFX_PASSWORD="pfx-pass",
                TCRA_PFX_PATH=pfx_path,
                TCRA_SIGNATURE_HEADER="X-Custom-TCRA-Signature",
            ):
                client = TcraClient(config=self.config)
                headers = client._build_headers(body)
        finally:
            if os.path.exists(pfx_path):
                os.remove(pfx_path)

        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertIn("X-Custom-TCRA-Signature", headers)

        signature = base64.b64decode(headers["X-Custom-TCRA-Signature"], validate=True)
        cert.public_key().verify(signature, body.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())

    def test_build_headers_fails_when_pfx_missing(self):
        with override_settings(
            TCRA_PFX_PASSWORD="",
            TCRA_PFX_PATH="/tmp/tcra_private_test_client_missing.pfx",
        ):
            client = TcraClient(config=self.config)
            with self.assertRaises(TcraClientError):
                client._build_headers("{}")

    def test_build_headers_from_mounted_pfx_path(self):
        cert, pfx_bytes = _build_pkcs12_material("pfx-pass")
        pfx_path = "/tmp/tcra_private_test_client_mounted.pfx"
        with open(pfx_path, "wb") as pfx_file:
            pfx_file.write(pfx_bytes)

        body = json.dumps({"eventsList": []}, separators=(",", ":"), ensure_ascii=False)
        try:
            with override_settings(
                TCRA_PFX_PASSWORD="pfx-pass",
                TCRA_PFX_PATH=pfx_path,
                TCRA_SIGNATURE_HEADER="X-TCRA-Signature",
            ):
                client = TcraClient(config=self.config)
                headers = client._build_headers(body)
        finally:
            if os.path.exists(pfx_path):
                os.remove(pfx_path)

        signature = base64.b64decode(headers["X-TCRA-Signature"], validate=True)
        cert.public_key().verify(signature, body.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())

    @patch("tcra_integration.services.client.requests.post")
    def test_post_json_signs_exact_sent_bytes(self, mocked_post):
        cert, pfx_bytes = _build_pkcs12_material("pfx-pass")
        pfx_path = f"/tmp/tcra_private_test_client_{uuid.uuid4().hex}.pfx"
        with open(pfx_path, "wb") as pfx_file:
            pfx_file.write(pfx_bytes)

        payload = {"eventsList": [{"msgInfo": {"msgId": "1"}, "txnInfo": {"name": "Málaga"}}]}
        expected_body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        mocked_post.return_value = Mock(status_code=200, text="ok")

        try:
            with override_settings(
                TCRA_PFX_PASSWORD="pfx-pass",
                TCRA_PFX_PATH=pfx_path,
                TCRA_SIGNATURE_HEADER="X-TCRA-Signature",
            ):
                client = TcraClient(config=self.config)
                client.post_json("/v1/api/events", payload)
        finally:
            if os.path.exists(pfx_path):
                os.remove(pfx_path)

        args, kwargs = mocked_post.call_args
        self.assertEqual(args[0], "https://example.com/v1/api/events")
        self.assertEqual(kwargs["data"], expected_body)
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")

        signature = base64.b64decode(kwargs["headers"]["X-TCRA-Signature"], validate=True)
        cert.public_key().verify(signature, kwargs["data"].encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
