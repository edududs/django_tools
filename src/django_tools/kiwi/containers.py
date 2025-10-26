"""Dependency Injection containers for Kiwi module."""

from celery import Celery
from dependency_injector import containers, providers
from kombu import Exchange, Queue

from django_tools.settings import DjangoSettingsBaseModel


def configure_celery(
    config: object,
    app_name: str = "django_tools",
) -> Celery:
    celery_app = Celery(app_name)
    users_exchange = Exchange("users_exchange", type="fanout")
    celery_app.conf.task_queues = (
        Queue("users_queue", exchange=users_exchange, routing_key=""),
        Queue("notifications_queue", exchange=users_exchange, routing_key=""),
        Queue("default", routing_key="default"),
    )
    celery_app.config_from_object(config, namespace="CELERY")
    celery_app.autodiscover_tasks()
    return celery_app


class KiwiContainer(containers.DeclarativeContainer):
    """Container for Kiwi queue management dependencies."""

    config = providers.Configuration()

    celery_config = providers.Dict(
        broker_url=config.kiwi_django_settings.effective_broker_url,
        result_backend=config.kiwi_django_settings.celery_result_backend,
        timezone=config.kiwi_django_settings.celery_timezone,
        task_serializer=config.kiwi_django_settings.celery_task_serializer,
        result_serializer=config.kiwi_django_settings.celery_result_serializer,
        accept_content=config.kiwi_django_settings.celery_accept_content,
        task_track_started=config.kiwi_django_settings.celery_task_track_started,
        task_time_limit=config.kiwi_django_settings.celery_task_time_limit,
        task_soft_time_limit=config.kiwi_django_settings.celery_task_soft_time_limit,
        worker_prefetch_multiplier=config.kiwi_django_settings.celery_worker_prefetch_multiplier,
        worker_max_tasks_per_child=config.kiwi_django_settings.celery_worker_max_tasks_per_child,
    )

    celery_app = providers.Singleton(configure_celery, config=config)


if __name__ == "__main__":
    config = {"kiwi_django_settings": DjangoSettingsBaseModel(), "app_name": "user"}
    container = KiwiContainer()
    container.config.from_dict(config)
    celery_app = container.celery_app()
    print(celery_app)
    print(celery_app.conf)
    print(celery_app.conf.task_queues)
    print(celery_app.conf.task_routes)
    print(celery_app.conf.task_default_queue)
