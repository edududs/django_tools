import json
from contextlib import suppress
from pathlib import Path

from pydantic import BaseModel, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .consts import DJANGO_SETTINGS_KEYS


class DatabaseSettings(BaseModel):
    """Database configuration using Pydantic BaseSettings.

    Loads values from a .env file located at the project root (where manage.py is).
    """

    engine: str = Field(default="django.db.backends.sqlite3")
    name: str = Field(default="db.sqlite3")
    user: str | None = Field(default=None)
    password: str | None = Field(default=None)
    host: str | None = Field(default=None)
    port: int | None = Field(default=None)


class DjangoSettings(BaseSettings):
    """Main Django settings using Pydantic v2."""

    def __init__(self, *args, **kwargs):
        env_file = kwargs.pop("env_file")
        if env_file:
            config = SettingsConfigDict(
                env_file=env_file,
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore",
            )
            path_env = str(Path(env_file).parent)
        else:
            path_env = str(Path(kwargs.pop("env_dir") or (args[0] if args else ".")))
            config = SettingsConfigDict(
                env_file=f"{path_env}/.env",
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore",
            )
        type(self).model_config = config
        type(self).path_env = path_env  # type: ignore[attr-defined]
        super().__init__()

    # Configurações de segurança
    secret_key: str = Field(default="django-insecure")
    debug: bool = Field(default=True)
    allowed_hosts_raw: str | list[str] = Field(
        default=["*"],
        alias="ALLOWED_HOSTS",
    )

    @computed_field  # type: ignore[misc]
    @property
    def allowed_hosts(self) -> list[str]:
        """Interpreta ALLOWED_HOSTS de string para lista."""
        if not self.allowed_hosts_raw or str(self.allowed_hosts_raw).strip() == "":
            return ["*"]

        text = str(self.allowed_hosts_raw).strip()

        # Tenta primeiro interpretar como array JSON
        if text.startswith("[") and text.endswith("]"):
            with suppress(Exception):
                data = json.loads(text)
                if isinstance(data, list):
                    return [str(x).strip() for x in data]

        # Fallback para parsing CSV
        hosts = [h.strip() for h in text.split(",") if h.strip()]
        return hosts or ["*"]

    # Configurações de aplicação
    @property
    def default_installed_apps(self):
        return [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ]

    @property
    def default_middleware(self):
        return [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]

    # Configurações de banco de dados
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Configurações de internacionalização
    language_code: str = Field(default="pt-br")
    time_zone: str = Field(default="UTC")
    use_i18n: bool = Field(default=True)
    use_tz: bool = Field(default=True)

    # Configurações de chave primária padrão
    default_auto_field: str = Field(default="django.db.models.BigAutoField")

    # Configurações de logging
    default_logging_config: str = "logging.config.dictConfig"
    template_backend: str = Field(default="django.template.backends.django.DjangoTemplates")
    template_dirs: list[str] = Field(default_factory=list)
    template_app_dirs: bool = Field(default=True)
    template_context_processors: list[str] = Field(
        default_factory=lambda: [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]
    )

    # Celery
    celery_broker_url: str = Field(
        default="amqp://admin:admin@localhost:5672/",
        alias="CELERY_BROKER_URL",
        description="URL do broker de mensagens do Celery (RabbitMQ)",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        alias="CELERY_RESULT_BACKEND",
        description="Backend para armazenar resultados das tarefas (Redis)",
    )
    celery_timezone: str = Field(
        default="UTC",
        alias="CELERY_TIMEZONE",
        description="Fuso horário para agendamento de tarefas",
    )
    celery_task_serializer: str = Field(
        default="json",
        alias="CELERY_TASK_SERIALIZER",
        description="Formato de serialização para envio de tarefas (json, pickle, yaml)",
    )
    celery_result_serializer: str = Field(
        default="json",
        alias="CELERY_RESULT_SERIALIZER",
        description="Formato de serialização para resultados das tarefas",
    )
    celery_accept_content: list[str] = Field(
        default=["json"],
        alias="CELERY_ACCEPT_CONTENT",
        description="Formatos de conteúdo aceitos nas mensagens",
    )
    celery_task_track_started: bool = Field(
        default=True,
        alias="CELERY_TASK_TRACK_STARTED",
        description="Rastrear quando uma tarefa começou a executar",
    )
    celery_task_time_limit: int = Field(
        default=3600,
        alias="CELERY_TASK_TIME_LIMIT",
        description="Tempo máximo que uma tarefa pode executar (segundos)",
    )
    celery_task_soft_time_limit: int = Field(
        default=3300,
        alias="CELERY_TASK_SOFT_TIME_LIMIT",
        description="Tempo limite soft para limpeza graciosa antes do hard limit (segundos)",
    )
    celery_worker_prefetch_multiplier: int = Field(
        default=1,
        alias="CELERY_WORKER_PREFETCH_MULTIPLIER",
        description="Quantas tarefas um worker pode prefetch simultaneamente",
    )
    celery_worker_max_tasks_per_child: int = Field(
        default=1000,
        alias="CELERY_WORKER_MAX_TASKS_PER_CHILD",
        description="Máximo de tarefas por processo worker antes de reiniciar",
    )

    @computed_field  # type: ignore[misc]
    @property
    def celery_config(self) -> dict:
        return {
            "broker_url": self.celery_broker_url,
            "result_backend": self.celery_result_backend,
            "timezone": self.celery_timezone,
            "task_serializer": self.celery_task_serializer,
            "result_serializer": self.celery_result_serializer,
            "accept_content": self.celery_accept_content,
            "task_track_started": self.celery_task_track_started,
            "task_time_limit": self.celery_task_time_limit,
            "task_soft_time_limit": self.celery_task_soft_time_limit,
            "worker_prefetch_multiplier": self.celery_worker_prefetch_multiplier,
            "worker_max_tasks_per_child": self.celery_worker_max_tasks_per_child,
        }

    @property
    def templates(self):
        return [
            {
                "BACKEND": self.template_backend,
                "DIRS": self.template_dirs,
                "APP_DIRS": self.template_app_dirs,
                "OPTIONS": {
                    "context_processors": self.template_context_processors,
                },
            },
        ]

    @property
    def default_logging(self):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
                    "style": "{",
                },
                "simple": {
                    "format": "{levelname} {message}",
                    "style": "{",
                },
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "loggers": {
                "django": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }

    # Configurações de senha
    @property
    def default_auth_password_validators(self):
        return [
            {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
            {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
            {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        ]

    @computed_field  # type: ignore[misc]
    @property
    def databases(self) -> dict:
        db_settings = self.database
        db_config = {"ENGINE": getattr(db_settings, "engine", None)}

        # SQLite
        if getattr(db_settings, "engine", None) == "django.db.backends.sqlite3":
            db_config["NAME"] = str(
                Path(self.__class__.path_env) / getattr(db_settings, "name", "db.sqlite3")  # type: ignore[attr-defined]
            )
        else:
            # PostgreSQL, MySQL, etc.
            keys = ["name", "user", "password", "host", "port"]
            db_config.update(
                {k.upper(): v for k in keys if (v := getattr(db_settings, k, None)) is not None}
            )
        return {"default": db_config}

    def to_dict(self) -> dict:
        """Retorna configuração do Django como um dicionário."""
        result = {}
        for key in DJANGO_SETTINGS_KEYS:
            value = getattr(self, key.lower(), None)
            if value is not None:
                result[key] = value
        return result

    api_name: str = Field(default="core")
