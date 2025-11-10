from celery import Celery
from dependency_injector import containers, providers

from django_tools.settings.base.infra.settings_celery import CelerySettings


def get_celery_app(app_name: str = "django_tools", config: CelerySettings | None = None) -> Celery:
    """Cria e configura uma instância do Celery."""
    app = Celery(app_name)
    if config:
        # Converte CelerySettings para dict usando aliases (CELERY_*) para compatibilidade com Celery
        celery_config = config.model_dump(by_alias=True, exclude_none=True)
        app.config_from_object(celery_config, namespace="CELERY")
    else:
        app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
    return app


class KiwiContainer(containers.DeclarativeContainer):
    """Container for Kiwi queue management dependencies.

    Uso:
        container = KiwiContainer()
        # Opcional: carregar configurações no config provider para acesso dinâmico
        container.config.from_pydantic(container.celery_settings())
        # Usar o celery_app singleton
        app = container.celery_app()
    """

    # Factory provider cria a instância do CelerySettings (carrega de .env automaticamente)
    celery_settings = providers.Singleton(CelerySettings)

    # Configuration provider para acesso dinâmico às configurações via from_pydantic()
    # Carregue manualmente com: container.config.from_pydantic(container.celery_settings())
    config = providers.Configuration()
    config.from_pydantic(celery_settings)

    # Singleton do Celery app usando as configurações do CelerySettings
    celery_app = providers.Singleton(
        get_celery_app,
        app_name="django_tools",
        config=celery_settings,
    )
