from __future__ import annotations

from typing import Any

from celery import Celery
from dependency_injector import providers


def print_obj_and_type(obj: Any, label: str = "Objeto"):
    print("-" * 50)
    print(f"{label}: {obj!r}")
    print(f"Tipo de {label.lower()}: {type(obj)}")
    print("-" * 50)


def get_celery_app(name: str = "test_app"):
    app = Celery(name)
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
    return app


# Singleton provider usando a factory get_celery_app
celery_app_singleton = providers.Singleton(get_celery_app, name="singleton_app")

# Factory provider (cria uma nova aplicação Celery em cada chamada)
celery_app_factory = providers.Factory(get_celery_app, name="factory_app")


def test_singleton_provider():
    print("\n🧪 Testando Singleton Provider")
    app1 = celery_app_singleton()
    app2 = celery_app_singleton()
    print("Instâncias do singleton (devem ser iguais):")
    print(f"  app1 id: {id(app1)}")
    print(f"  app2 id: {id(app2)}")
    print(f"Mesma instância: {app1 is app2}")


def test_factory_provider():
    print("\n🧪 Testando Factory Provider")
    app1 = celery_app_factory()
    app2 = celery_app_factory()
    print("Instâncias do factory (devem ser diferentes):")
    print(f"  app1 id: {id(app1)}")
    print(f"  app2 id: {id(app2)}")
    print(f"Instâncias diferentes: {app1 is not app2}")


def test_configuration_provider():
    print("\n🧪 Testando Configuration Provider")
    config = providers.Configuration()
    config_dict = {
        "app_name": "MeuAppLindo",
        "version": "1.0.0",
        "enabled": True,
    }
    config.from_dict(config_dict)
    print_obj_and_type(config, label="Configuration Provider")
    print("⚙️  Configurações acessadas individualmente:")
    print(f"  app_name: {config.app_name()}")
    print(f"  version: {config.version()}")
    print(f"  enabled: {config.enabled()}")


def test_callable_provider():
    print("\n🧪 Testando Callable Provider")
    provider = providers.Callable(lambda x, y: x + y, 10, y=20)
    resultado = provider()
    print(f"Resultado da soma de 10 + 20 (via Callable Provider): {resultado}")


def run_all_tests():
    print("========== Demonstração dos Providers do dependency-injector ==========")
    test_singleton_provider()
    test_factory_provider()
    test_configuration_provider()
    test_callable_provider()
    print("=======================================================================")


if __name__ == "__main__":
    run_all_tests()
