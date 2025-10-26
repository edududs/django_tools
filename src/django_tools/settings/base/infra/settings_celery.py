from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from datetime import timedelta

    from celery.schedules import crontab, schedule
    from kombu import Queue


# ---- Type aliases for task routing ------------------------------------------
class RouteOptions(TypedDict, total=False):
    """Routing options for Celery tasks."""

    queue: str
    routing_key: str
    exchange: str


type RouteReturn = str | RouteOptions
type RouteCallable = Callable[
    [str, Sequence[object], Mapping[str, object], Mapping[str, object]],
    RouteReturn,
]
type TaskRoutes = Mapping[str, str | RouteOptions] | Sequence[str | RouteCallable]


# ---- Type aliases for Beat schedule -----------------------------------------
class BeatEntry(TypedDict, total=False):
    """Entry for the Celery Beat schedule."""

    task: str  # required in practice
    schedule: schedule | crontab | timedelta | float
    args: Sequence[object]
    kwargs: Mapping[str, object]
    options: Mapping[str, object]


type BeatSchedule = Mapping[str, BeatEntry]


class CelerySettings(BaseSettings):
    """Celery settings for CELERY_ .env prefix."""

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        serialize_by_alias=True,
    )

    broker_url: str | None = Field(
        default=None,
        alias="CELERY_BROKER_URL",
        description="Broker URL for messages (e.g., Redis, RabbitMQ).",
    )

    result_backend: str | None = Field(
        default=None,
        alias="CELERY_RESULT_BACKEND",
        description="Backend to store task results (e.g., redis://localhost:6379/1, db+sqlite:///results.db, django-db).",
    )
    timezone: str = Field(
        default="UTC",
        alias="CELERY_TIMEZONE",
        description="Timezone for Celery date/times.",
    )
    enable_utc: bool = Field(
        default=True,
        description="Enable/disable UTC conversion.",
    )

    # Task configuration
    accept_content: Sequence[Literal["json", "pickle", "yaml", "msgpack"]] = Field(
        default_factory=lambda: ["json"],
        alias="CELERY_ACCEPT_CONTENT",
        description="List of accepted serialized content-types.",
    )
    task_serializer: Literal["json", "pickle", "yaml", "msgpack"] = Field(
        default="json",
        alias="CELERY_TASK_SERIALIZER",
        description="Default serializer for task messages (json, pickle, etc).",
    )
    task_compression: Literal["gzip", "bzip2"] | None = Field(
        default=None,
        alias="CELERY_TASK_COMPRESSION",
        description="Compression method for task messages (gzip, bzip2).",
    )
    task_track_started: bool = Field(
        default=True,
        alias="CELERY_TASK_TRACK_STARTED",
        description="If enabled, records when a task starts in results.",
    )
    task_ignore_result: bool = Field(
        default=False,
        alias="CELERY_TASK_IGNORE_RESULT",
        description="If True, ignores task results to save resources.",
    )
    task_eager_propagates: bool = Field(
        default=True,
        alias="CELERY_TASK_EAGER_PROPAGATES",
        description="With CELERY_TASK_ALWAYS_EAGER=True, exceptions are propagated immediately (useful for testing).",
    )
    task_always_eager: bool = Field(
        default=False,
        alias="CELERY_TASK_ALWAYS_EAGER",
        description="Executes tasks locally/synchronously (useful for tests).",
    )
    task_time_limit: int | None = Field(
        default=None,
        alias="CELERY_TASK_TIME_LIMIT",
        description="Hard time limit (seconds) for task execution.",
    )
    task_soft_time_limit: int | None = Field(
        default=None,
        alias="CELERY_TASK_SOFT_TIME_LIMIT",
        description="Soft time limit (seconds) for task execution.",
    )
    task_reject_on_worker_lost: bool = Field(
        default=True,
        alias="CELERY_TASK_REJECT_ON_WORKER_LOST",
        description="Rejects tasks if the worker is lost.",
    )

    # Routing configuration
    task_queues: tuple[Queue, ...] | None = Field(
        default=None,
        description="Tuple of (kombu.Queue) objects Celery will monitor. Should not come from .env.",
    )
    task_routes: TaskRoutes | None = Field(
        default=None,
        description="Maps specific tasks to queues/routers. Should not be loaded from .env if using callables.",
    )
    task_default_queue: str = Field(
        default="default",
        alias="CELERY_TASK_DEFAULT_QUEUE",
        description="Default queue for tasks without an explicit route.",
    )
    task_default_exchange: str = Field(
        default="default",
        alias="CELERY_TASK_DEFAULT_EXCHANGE",
        description="Default exchange for tasks.",
    )
    task_default_routing_key: str = Field(
        default="default",
        alias="CELERY_TASK_DEFAULT_ROUTING_KEY",
        description="Default routing key.",
    )
    task_create_missing_queues: bool = Field(
        default=True,
        alias="CELERY_TASK_CREATE_MISSING_QUEUES",
        description="If True, automatically creates missing queues/exchanges.",
    )

    # Worker configuration
    worker_concurrency: int | None = Field(
        default=None,
        alias="CELERY_WORKER_CONCURRENCY",
        description="Number of concurrent worker processes/threads.",
    )
    worker_pool: Literal["prefork", "solo", "threads", "eventlet", "gevent"] | None = Field(
        default=None,
        alias="CELERY_WORKER_POOL",
        description="Worker pool implementation (e.g., prefork, threads).",
    )
    worker_prefetch_multiplier: int = Field(
        default=1,
        ge=1,
        alias="CELERY_WORKER_PREFETCH_MULTIPLIER",
        description="Number of tasks prefetched by the worker from the broker.",
    )
    worker_max_tasks_per_child: int = Field(
        default=1000,
        ge=0,
        alias="CELERY_WORKER_MAX_TASKS_PER_CHILD",
        description="Max number of tasks per child process before restart (0 = unlimited).",
    )
    worker_lost_wait: float | None = Field(
        default=None,
        alias="CELERY_WORKER_LOST_WAIT",
        description="Seconds before the worker considers a task as lost.",
    )

    # Celery Beat configuration
    beat_schedule: BeatSchedule | None = Field(
        default=None,
        description="Defines scheduled periodic tasks. Should not be read from .env.",
    )
    beat_schedule_filename: str | None = Field(
        default=None,
        alias="CELERY_BEAT_SCHEDULE_FILENAME",
        description="Filename for Celery Beat persistent schedule state.",
    )
    beat_scheduler: str | None = Field(
        default=None,
        alias="CELERY_BEAT_SCHEDULER",
        description="Scheduler to use (e.g., django_celery_beat.schedulers:DatabaseScheduler).",
    )

    # Cache configuration
    cache_backend: str | None = Field(
        default=None,
        alias="CELERY_CACHE_BACKEND",
        description="Backend to use for Celery cache, can integrate with Django caching.",
    )
