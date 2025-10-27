from celery import Celery

from django_tools.settings.base.infra.settings_celery import CelerySettings


def create_celery_instance(app_name: str, config: CelerySettings | None = None) -> Celery:
    app = Celery(app_name)
    if config:
        app.config_from_object(config, namespace="CELERY")
        app.autodiscover_tasks()
        return app
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
    return app
