import os
import sys
from pathlib import Path

from django.conf import Settings


def setup_django(
    project_root: str = "",
    app_name: str = "core",
) -> None:
    """Configura o ambiente Django para execução standalone.

    Args:
        project_root (str): Caminho absoluto ou relativo para a raiz do projeto Django.
        app_name (str): Nome do app principal (usado para o módulo de settings).

    """
    # Adiciona o diretório do projeto ao sys.path
    sys.path.insert(0, str(Path(project_root).resolve()))

    # Define a variável de ambiente para o módulo de settings do Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")

    # Força o uso de DSN para scripts standalone
    os.environ["TENANCY_USE_DSN"] = "1"
    import django

    django.setup()


def setup_django_if_needed(settings: type[Settings] | None = None, app_name: str = "core") -> None:
    """Configura o ambiente Django caso ainda não esteja configurado.

    Args:
        settings (type[Settings] | None): Instância de settings do Django, se disponível.
        app_name (str): Nome do app principal (usado para o módulo de settings).

    """
    # Se já estiver configurado, não faz nada
    if settings and settings.configured:
        return
    try:
        from django.conf import settings as django_settings

        # Verifica se o Django já está configurado
        if not django_settings.configured:
            raise ImportError("Django não está configurado")
    except (ImportError, AttributeError):
        # Se não estiver configurado, executa a configuração
        setup_django(app_name=app_name)
