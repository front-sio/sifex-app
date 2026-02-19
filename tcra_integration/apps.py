import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class TcraIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tcra_integration"

    def ready(self):
        from tcra_integration.services.crypto import bootstrap_pfx_file

        # In local/test environments we allow startup without TCRA secrets.
        if getattr(settings, "DEBUG", True) and not getattr(settings, "TCRA_PFX_PATH", ""):
            return

        try:
            bootstrap_pfx_file()
        except Exception:
            logger.exception("Failed bootstrapping TCRA PKCS#12 material")
            if not getattr(settings, "DEBUG", True):
                raise
