from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.conf import Settings


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
        if django_settings.configured:
            return  # ✅ Django já está configurado, não precisa fazer nada

    except (ImportError, AttributeError):
        pass  # Django não está disponível, precisa configurar

    # Se chegou até aqui, Django não está configurado - vamos configurar
    setup_django(app_name=app_name)


def setup_django(
    project_root: str = "",
    app_name: str = "core",
) -> None:
    """Configura o ambiente Django para execução standalone.

    Args:
        project_root (str): Caminho absoluto ou relativo para a raiz do projeto Django.
        app_name (str): Nome do app principal (usado para o módulo de settings).

    """
    # Se project_root não foi fornecido, tenta detectar automaticamente
    if not project_root:
        # Procura pelo diretório atual ou pai que contenha manage.py
        current_path = Path.cwd()
        for path in [current_path, *list(current_path.parents)]:
            if (path / "manage.py").exists():
                project_root = str(path)
                break
        else:
            # Se não encontrou manage.py, usa o diretório atual
            project_root = str(current_path)

    # Adiciona o diretório do projeto ao sys.path
    project_path = Path(project_root).resolve()
    if str(project_path) not in sys.path:
        sys.path.insert(0, str(project_path))

    # Define a variável de ambiente para o módulo de settings do Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")

    import django

    django.setup()
