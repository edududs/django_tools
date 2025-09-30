# pylint: disable=unused-import, wildcard-import

import logging
from contextlib import suppress

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("apis_ecossistem.common")

# The logger is available for submodules to use:
# from apis_ecossistem.common import logger


class CommonSettingsConfig(AppConfig):
    """Configuração da aplicação Django Common Settings."""

    name = "common.settings"
    label = "common_settings"
    verbose_name = _("Common Settings")

    def ready(self) -> None:
        """Método executado quando o Django está pronto."""
        # Importa as configurações para garantir que estejam disponíveis
        with suppress(ImportError):
            from .settings import (
                utils,
            )
            # Configurações são carregadas automaticamente pelo Pydantic


# Configuração padrão para facilitar importação
default_app_config = "common.settings.CommonSettingsConfig"
