import base64

from django.test import TestCase

from tcra_integration.models import TcraEndpointConfig
from tcra_integration.services.client import TcraClient


class TcraClientAuthHeaderTests(TestCase):
    def test_api_key_header(self):
        config = TcraEndpointConfig.objects.create(
            base_url="https://example.com",
            auth_type=TcraEndpointConfig.AuthType.API_KEY,
            api_key="secret-key",
        )
        client = TcraClient(config=config)
        headers = client.build_auth_headers()
        self.assertEqual(headers.get("X-API-Key"), "secret-key")

    def test_basic_auth_header(self):
        config = TcraEndpointConfig.objects.create(
            base_url="https://example.com",
            auth_type=TcraEndpointConfig.AuthType.BASIC,
            username="user",
            password="pass",
        )
        client = TcraClient(config=config)
        headers = client.build_auth_headers()
        expected = base64.b64encode(b"user:pass").decode("ascii")
        self.assertEqual(headers.get("Authorization"), f"Basic {expected}")
