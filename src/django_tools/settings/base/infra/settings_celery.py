from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    """Configurações do Celery com prefixo CELERY_ do .env"""  # noqa: D400, D415

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        serialize_by_alias=True,
    )

    broker_url: str | None = Field(
        default=None,
        alias="CELERY_BROKER_URL",
        description="A URL do broker de mensagens (ex: Redis, RabbitMQ)",
    )

    result_backend: str | None = Field(
        default=None,
        alias="CELERY_RESULT_BACKEND",
        description="Backend para armazenar os resultados das tarefas (ex: redis://localhost:6379/1, db+sqlite:///results.db, django-db)",
    )
    timezone: str = Field(
        default="UTC",
        alias="CELERY_TIMEZONE",
        description="Fuso horário para datas/horas do Celery.",
    )
    enable_utc: bool = Field(
        default=True,
        description="Ativa/desativa conversão para UTC.",
    )

    # Configurações de tarefa
    accept_content: list[str] = Field(
        default_factory=lambda: ["json"],
        alias="CELERY_ACCEPT_CONTENT",
        description="Lista de tipos de conteúdo serializados aceitáveis.",
    )
    task_serializer: str = Field(
        default="json",
        alias="CELERY_TASK_SERIALIZER",
        description="Serializador padrão para mensagens de tarefa (json, pickle).",
    )
    task_compression: str | None = Field(
        default=None,
        alias="CELERY_TASK_COMPRESSION",
        description="Método de compressão para as mensagens de tarefa (gzip, bzip2).",
    )
    task_track_started: bool = Field(
        default=True,
        alias="CELERY_TASK_TRACK_STARTED",
        description="Se habilitado, registra início da tarefa nos resultados.",
    )
    task_ignore_result: bool = Field(
        default=False,
        alias="CELERY_TASK_IGNORE_RESULT",
        description="Se True, ignora resultados das tarefas para economizar recursos.",
    )
    task_eager_propagates: bool = Field(
        default=True,
        alias="CELERY_TASK_EAGER_PROPAGATES",
        description="Com CELERY_TASK_ALWAYS_EAGER=True, propaga exceções imediatamente (para testes).",
    )
    task_always_eager: bool = Field(
        default=False,
        alias="CELERY_TASK_ALWAYS_EAGER",
        description="Executa tarefas localmente/sincronamente (útil para testes).",
    )
    task_time_limit: int | None = Field(
        default=None,
        alias="CELERY_TASK_TIME_LIMIT",
        description="Tempo limite rígido (segundos) para execução de uma tarefa.",
    )
    task_soft_time_limit: int | None = Field(
        default=None,
        alias="CELERY_TASK_SOFT_TIME_LIMIT",
        description="Tempo limite flexível (segundos).",
    )
    task_reject_on_worker_lost: bool = Field(
        default=True,
        alias="CELERY_TASK_REJECT_ON_WORKER_LOST",
        description="Rejeita tarefas caso worker se perca.",
    )

    # Configurações de roteamento
    task_queues: list[Any] | None = Field(
        default=None,
        alias="CELERY_TASK_QUEUES",
        description="Lista ou tupla de filas que o Celery monitora, permite definição personalizada.",
    )
    task_routes: dict[str, Any] | None = Field(
        default=None,
        alias="CELERY_TASK_ROUTES",
        description="Mapeia tarefas específicas para filas específicas.",
    )
    task_default_queue: str = Field(
        default="default",
        alias="CELERY_TASK_DEFAULT_QUEUE",
        description="Fila padrão para tarefas sem rota definida.",
    )
    task_default_exchange: str = Field(
        default="default",
        alias="CELERY_TASK_DEFAULT_EXCHANGE",
        description="Exchange padrão para tarefas.",
    )
    task_default_routing_key: str = Field(
        default="default",
        alias="CELERY_TASK_DEFAULT_ROUTING_KEY",
        description="Routing key padrão.",
    )
    task_create_missing_queues: bool = Field(
        default=True,
        alias="CELERY_TASK_CREATE_MISSING_QUEUES",
        description="Se True, cria filas/exchanges ausentes automaticamente.",
    )

    # Configurações do worker
    worker_concurrency: int | None = Field(
        default=None,
        alias="CELERY_WORKER_CONCURRENCY",
        description="Número de processos/threads concorrentes para executar tarefas.",
    )
    worker_pool: str | None = Field(
        default=None,
        alias="CELERY_WORKER_POOL",
        description="Implementação do pool de processos (ex: prefork, threads).",
    )
    worker_prefetch_multiplier: int = Field(
        default=1,
        alias="CELERY_WORKER_PREFETCH_MULTIPLIER",
        description="Número de tarefas pré-buscadas pelo worker do broker.",
    )
    worker_max_tasks_per_child: int = Field(
        default=1000,
        alias="CELERY_WORKER_MAX_TASKS_PER_CHILD",
        description="Máx. de tarefas por processo filho antes do restart.",
    )
    worker_lost_wait: int | None = Field(
        default=None,
        alias="CELERY_WORKER_LOST_WAIT",
        description="Tempo (segundos) antes do worker marcar tarefa como perdida.",
    )

    # Configurações do Celery Beat
    beat_schedule: dict[str, Any] | None = Field(
        default=None,
        alias="CELERY_BEAT_SCHEDULE",
        description="Define tarefas periòdicas agendadas.",
    )
    beat_schedule_filename: str | None = Field(
        default=None,
        alias="CELERY_BEAT_SCHEDULE_FILENAME",
        description="Nome do arquivo de estado do Celery Beat.",
    )
    beat_scheduler: str | None = Field(
        default=None,
        alias="CELERY_BEAT_SCHEDULER",
        description="Agendador a ser usado (ex: django_celery_beat.schedulers:DatabaseScheduler).",
    )

    # Configurações de cache
    cache_backend: str | None = Field(
        default=None,
        alias="CELERY_CACHE_BACKEND",
        description="Backend de cache para o Celery, pode integrar ao cache do Django.",
    )
