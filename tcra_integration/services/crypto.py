import base64
import binascii
import logging
import os
from functools import lru_cache
from typing import Optional, Tuple

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dsa, ec, padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from django.conf import settings

logger = logging.getLogger(__name__)


class TcraCryptoError(Exception):
    pass


def _signature_header_name() -> str:
    configured = (
        getattr(settings, "TCRA_SIGNATURE_HEADER", "")
        or getattr(settings, "TCRA_WEBHOOK_SIGNATURE_HEADER", "")
    ).strip()
    if not configured:
        raise TcraCryptoError("TCRA_SIGNATURE_HEADER is not configured")
    return configured


def _resolve_pfx_path(path: str) -> str:
    if not path:
        raise TcraCryptoError("TCRA_PFX_PATH is not configured")
    if not os.path.isfile(path):
        raise TcraCryptoError(f"PFX file not found at {path}")
    return path


@lru_cache(maxsize=8)
def _load_signing_material(pfx_password: str, pfx_path: str) -> Tuple[object, Optional[x509.Certificate]]:
    path = _resolve_pfx_path(path=pfx_path)
    password = pfx_password.encode("utf-8") if pfx_password else None

    with open(path, "rb") as pfx_file:
        key, cert, _extra = pkcs12.load_key_and_certificates(pfx_file.read(), password)

    if key is None:
        raise TcraCryptoError("PKCS#12 archive does not contain a private key")
    return key, cert


def _private_key() -> object:
    return _load_signing_material(
        pfx_password=getattr(settings, "TCRA_PFX_PASSWORD", ""),
        pfx_path=getattr(settings, "TCRA_PFX_PATH", ""),
    )[0]


def _signature_bytes(data: bytes) -> bytes:
    key = _private_key()
    if not isinstance(key, rsa.RSAPrivateKey):
        raise TcraCryptoError(f"Unsupported private key type: {type(key).__name__}. RSA is required.")
    return key.sign(data, padding.PKCS1v15(), hashes.SHA256())


def sign_request_body(data: bytes) -> str:
    signature = _signature_bytes(data)
    return base64.b64encode(signature).decode("ascii")


def _parse_certificate_bytes(cert_bytes: bytes) -> x509.Certificate:
    try:
        return x509.load_pem_x509_certificate(cert_bytes)
    except ValueError:
        try:
            return x509.load_der_x509_certificate(cert_bytes)
        except ValueError as exc:
            raise TcraCryptoError("Webhook certificate is not valid PEM or DER") from exc


def _parse_public_key_bytes(key_bytes: bytes):
    try:
        return serialization.load_pem_public_key(key_bytes)
    except ValueError:
        try:
            return serialization.load_der_public_key(key_bytes)
        except ValueError as exc:
            raise TcraCryptoError("Webhook public key is not valid PEM or DER") from exc


@lru_cache(maxsize=8)
def _load_webhook_public_key(
    cert_b64: str,
    cert_pem: str,
    cert_path: str,
    key_b64: str,
    key_pem: str,
    key_path: str,
) -> object:
    if key_b64:
        try:
            key_bytes = base64.b64decode(key_b64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise TcraCryptoError("TCRA_WEBHOOK_PUBLIC_KEY_B64 is not valid base64") from exc
        return _parse_public_key_bytes(key_bytes)

    if key_pem:
        return _parse_public_key_bytes(key_pem.encode("utf-8"))

    if key_path:
        with open(key_path, "rb") as key_file:
            return _parse_public_key_bytes(key_file.read())

    if cert_b64:
        try:
            cert_bytes = base64.b64decode(cert_b64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise TcraCryptoError("TCRA_WEBHOOK_PUBLIC_CERT_B64 is not valid base64") from exc
        return _parse_certificate_bytes(cert_bytes).public_key()

    if cert_pem:
        return _parse_certificate_bytes(cert_pem.encode("utf-8")).public_key()

    if cert_path:
        with open(cert_path, "rb") as cert_file:
            return _parse_certificate_bytes(cert_file.read()).public_key()

    raise TcraCryptoError("No webhook public certificate or key configured")


def _webhook_public_key() -> object:
    return _load_webhook_public_key(
        cert_b64=getattr(settings, "TCRA_WEBHOOK_PUBLIC_CERT_B64", ""),
        cert_pem=getattr(settings, "TCRA_WEBHOOK_PUBLIC_CERT_PEM", ""),
        cert_path=getattr(settings, "TCRA_WEBHOOK_PUBLIC_CERT_PATH", ""),
        key_b64=getattr(settings, "TCRA_WEBHOOK_PUBLIC_KEY_B64", ""),
        key_pem=getattr(settings, "TCRA_WEBHOOK_PUBLIC_KEY_PEM", ""),
        key_path=getattr(settings, "TCRA_WEBHOOK_PUBLIC_KEY_PATH", ""),
    )


def verify_webhook_signature(data: bytes, provided_signature: Optional[str]) -> bool:
    if not provided_signature:
        return False

    try:
        signature = base64.b64decode(provided_signature, validate=True)
        public_key = _webhook_public_key()
    except (TcraCryptoError, binascii.Error, ValueError):
        return False

    try:
        if isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())
            return True
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            return True
        if isinstance(public_key, dsa.DSAPublicKey):
            public_key.verify(signature, data, hashes.SHA256())
            return True
        return False
    except InvalidSignature:
        return False


def signature_header_name() -> str:
    return _signature_header_name()


def bootstrap_pfx_file() -> None:
    _load_signing_material(
        pfx_password=getattr(settings, "TCRA_PFX_PASSWORD", ""),
        pfx_path=getattr(settings, "TCRA_PFX_PATH", ""),
    )
