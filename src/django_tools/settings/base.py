# pylint: disable=no-member
import json
from contextlib import suppress
from pathlib import Path
from typing import Any

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


class CelerySettings(BaseModel):
    """Celery configuration settings."""

    broker_url: str = Field(
        default="amqp://admin:admin@localhost:5672/",
        alias="CELERY_BROKER_URL",
        description="URL do broker de mensagens do Celery (RabbitMQ)",
    )
    result_backend: str = Field(
        default="redis://localhost:6379/2",
        alias="CELERY_RESULT_BACKEND",
        description="Backend para armazenar resultados das tarefas (Redis)",
    )
    timezone: str = Field(
        default="UTC",
        alias="CELERY_TIMEZONE",
        description="Fuso horário para agendamento de tarefas",
    )
    task_serializer: str = Field(
        default="json",
        alias="CELERY_TASK_SERIALIZER",
        description="Formato de serialização para envio de tarefas (json, pickle, yaml)",
    )
    result_serializer: str = Field(
        default="json",
        alias="CELERY_RESULT_SERIALIZER",
        description="Formato de serialização para resultados das tarefas",
    )
    accept_content: list[str] = Field(
        default=["json"],
        alias="CELERY_ACCEPT_CONTENT",
        description="Formatos de conteúdo aceitos nas mensagens",
    )
    task_track_started: bool = Field(
        default=True,
        alias="CELERY_TASK_TRACK_STARTED",
        description="Rastrear quando uma tarefa começou a executar",
    )
    task_time_limit: int = Field(
        default=3600,
        alias="CELERY_TASK_TIME_LIMIT",
        description="Tempo máximo que uma tarefa pode executar (segundos)",
    )
    task_soft_time_limit: int = Field(
        default=3300,
        alias="CELERY_TASK_SOFT_TIME_LIMIT",
        description="Tempo limite soft para limpeza graciosa antes do hard limit (segundos)",
    )
    worker_prefetch_multiplier: int = Field(
        default=1,
        alias="CELERY_WORKER_PREFETCH_MULTIPLIER",
        description="Quantas tarefas um worker pode prefetch simultaneamente",
    )
    worker_max_tasks_per_child: int = Field(
        default=1000,
        alias="CELERY_WORKER_MAX_TASKS_PER_CHILD",
        description="Máximo de tarefas por processo worker antes de reiniciar",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def config(self) -> dict[str, Any]:
        """Retorna configuração do Celery como dicionário."""
        return {
            "broker_url": self.broker_url,
            "result_backend": self.result_backend,
            "timezone": self.timezone,
            "task_serializer": self.task_serializer,
            "result_serializer": self.result_serializer,
            "accept_content": self.accept_content,
            "task_track_started": self.task_track_started,
            "task_time_limit": self.task_time_limit,
            "task_soft_time_limit": self.task_soft_time_limit,
            "worker_prefetch_multiplier": self.worker_prefetch_multiplier,
            "worker_max_tasks_per_child": self.worker_max_tasks_per_child,
        }


class RedisSettings(BaseModel):
    """Redis configuration settings."""

    host: str = Field(
        default="localhost",
        alias="REDIS_HOST",
        description="Host do servidor Redis",
    )
    port: int = Field(
        default=6379,
        alias="REDIS_PORT",
        description="Porta do servidor Redis",
    )
    db: int = Field(
        default=0,
        alias="REDIS_DB",
        description="Número do banco de dados Redis",
    )
    password: str | None = Field(
        default=None,
        alias="REDIS_PASSWORD",
        description="Senha do Redis (opcional)",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """URL completa do Redis."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def config(self) -> dict[str, Any]:
        """Configuração do Redis."""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "password": self.password,
        }


class TemplateSettings(BaseModel):
    """Template configuration settings."""

    backend: str = Field(default="django.template.backends.django.DjangoTemplates")
    dirs: list[str] = Field(default_factory=list)
    app_dirs: bool = Field(default=True)
    context_processors: list[str] = Field(
        default_factory=lambda: [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def config(self) -> list[dict[str, Any]]:
        """Retorna configuração de templates como lista de dicionários."""
        return [
            {
                "BACKEND": self.backend,
                "DIRS": self.dirs,
                "APP_DIRS": self.app_dirs,
                "OPTIONS": {
                    "context_processors": self.context_processors,
                },
            },
        ]


class SecuritySettings(BaseModel):
    """Security configuration settings."""

    secret_key: str = Field(default="django-insecure")
    debug: bool = Field(default=True)
    allowed_hosts_raw: str | list[str] = Field(
        default=["*"],
        alias="ALLOWED_HOSTS",
    )

    @computed_field  # type: ignore[prop-decorator]
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


class InternationalizationSettings(BaseModel):
    """Internationalization configuration settings."""

    language_code: str = Field(default="pt-br")
    time_zone: str = Field(default="UTC")
    use_i18n: bool = Field(default=True)
    use_tz: bool = Field(default=True)


class DjangoSettings(BaseSettings):
    """Main Django settings using Pydantic v2."""

    def __init__(self, *args, **kwargs) -> None:
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

    # Configurações organizadas em schemas
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    template: TemplateSettings = Field(default_factory=TemplateSettings)
    internationalization: InternationalizationSettings = Field(default_factory=InternationalizationSettings)

    # Configurações de aplicação
    @property
    def default_installed_apps(self) -> list[str]:
        return [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ]

    @property
    def default_middleware(self) -> list[str]:
        return [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]

    # Configurações de chave primária padrão
    default_auto_field: str = Field(default="django.db.models.BigAutoField")

    # Configurações de logging
    default_logging_config: str = "logging.config.dictConfig"

    # Propriedades computadas que delegam para os schemas
    @computed_field  # type: ignore[prop-decorator]
    @property
    def secret_key(self) -> str:
        """Chave secreta do Django."""
        return self.security.secret_key

    @computed_field  # type: ignore[prop-decorator]
    @property
    def debug(self) -> bool:
        """Modo debug do Django."""
        return self.security.debug

    @computed_field  # type: ignore[prop-decorator]
    @property
    def allowed_hosts(self) -> list[str]:
        """Hosts permitidos."""
        return self.security.allowed_hosts

    @computed_field  # type: ignore[prop-decorator]
    @property
    def language_code(self) -> str:
        """Código do idioma."""
        return self.internationalization.language_code

    @computed_field  # type: ignore[prop-decorator]
    @property
    def time_zone(self) -> str:
        """Fuso horário."""
        return self.internationalization.time_zone

    @computed_field  # type: ignore[prop-decorator]
    @property
    def use_i18n(self) -> bool:
        """Usar internacionalização."""
        return self.internationalization.use_i18n

    @computed_field  # type: ignore[prop-decorator]
    @property
    def use_tz(self) -> bool:
        """Usar timezone."""
        return self.internationalization.use_tz

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_config(self) -> dict[str, Any]:
        """Configuração do Celery."""
        return self.celery.config

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_url(self) -> str:
        """URL completa do Redis."""
        return self.redis.url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_config(self) -> dict[str, Any]:
        """Configuração do Redis."""
        return self.redis.config

    @computed_field  # type: ignore[prop-decorator]
    @property
    def templates(self) -> list[dict[str, Any]]:
        """Configuração de templates."""
        return self.template.config

    @property
    def default_logging(self) -> dict[str, Any]:
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
    def default_auth_password_validators(self) -> list[dict[str, str]]:
        return [
            {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
            {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
            {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        ]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def databases(self) -> dict[str, dict[str, Any]]:
        """Configuração de banco de dados."""
        db_settings = self.database
        db_config = {"ENGINE": db_settings.engine}

        # SQLite
        if db_settings.engine == "django.db.backends.sqlite3":
            db_config["NAME"] = str(
                Path(self.__class__.path_env) / db_settings.name  # type: ignore[attr-defined]
            )
        else:
            # PostgreSQL, MySQL, etc.
            keys = ["name", "user", "password", "host", "port"]
            db_config.update({k.upper(): v for k in keys if (v := getattr(db_settings, k, None)) is not None})
        return {"default": db_config}

    # Configurações específicas da aplicação
    api_name: str = Field(default="core")

    def to_dict(self) -> dict[str, Any]:
        """Retorna configuração do Django como um dicionário."""
        result = {}
        for key in DJANGO_SETTINGS_KEYS:
            value = getattr(self, key.lower(), None)
            if value is not None:
                result[key] = value
        return result
