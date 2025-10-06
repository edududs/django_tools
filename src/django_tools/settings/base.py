# pylint: disable=no-member
import json
from contextlib import suppress
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .consts import DJANGO_SETTINGS_KEYS


def build_settings_config(*args, env_file: str | None = None, **kwargs):
    """Build dynamic configuration to load .env files from different locations."""
    env_file = env_file or kwargs.pop("env_file", None)
    if env_file:
        config = SettingsConfigDict(
            env_file=env_file,
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )
        path_env = str(Path(env_file).parent)
    else:
        path_env = str(Path(kwargs.pop("env_dir", None) or (args[0] if args else ".")))
        config = SettingsConfigDict(
            env_file=f"{path_env}/.env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )
    return config, path_env


class DjangoSettings(BaseSettings):
    """Centralized Django settings using Pydantic v2.

    This class provides a comprehensive configuration system for Django applications
    that handles multiple aspects of application configuration through environment
    variables and .env files. It supports different .env files for different environments
    (e.g., .env.feed, .env.produtos).

    Key Features:
    - Database configuration (SQLite, PostgreSQL, MySQL, etc.)
    - Message broker setup (RabbitMQ, Redis, Kafka)
    - Celery task queue configuration
    - Redis cache and session storage
    - Django security and application settings
    - Template and internationalization settings
    - Comprehensive logging configuration

    Configuration Priority:
    1. Environment variables
    2. .env file specified in constructor
    3. Default values

    The class automatically detects broker types from URLs and provides computed
    properties for Django-compatible configuration dictionaries.

    Example:
        # Using environment variables
        settings = DjangoSettings()

        # Using specific .env file
        settings = DjangoSettings(env_file=".env.production")

        # Using directory-based .env discovery
        settings = DjangoSettings(env_dir="/path/to/config")

    """

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, *args, env_file: str | None = None, **kwargs) -> None:
        config, path_env = build_settings_config(*args, env_file=env_file, **kwargs)
        type(self).model_config = config
        type(self).path_env = path_env  # type: ignore[attr-defined]
        super().__init__()

    # ==================================================================================
    # DATABASE SETTINGS
    # Supports complete URL OR separate variables (URL takes priority)
    # ==================================================================================
    database_url: str | None = Field(
        default=None,
        alias="DATABASE_URL",
        description="Complete database URL (e.g., postgresql://user:pass@host:port/db)",
    )
    db_engine: str = Field(
        default="django.db.backends.sqlite3",
        description="Database engine",
    )
    db_name: str = Field(
        default="db.sqlite3",
        description="Database name",
    )
    db_user: str | None = Field(
        default=None,
        description="Database username",
    )
    db_password: str | None = Field(
        default=None,
        description="Database password",
    )
    db_host: str | None = Field(
        default=None,
        description="Database host",
    )
    db_port: int | None = Field(
        default=None,
        description="Database port",
    )

    # ==================================================================================
    # BROKER SETTINGS (RabbitMQ, Redis, Kafka, etc.)
    # Suporta URL completa OU variáveis separadas (URL tem prioridade)
    # ==================================================================================
    broker_url: str | None = Field(
        default=None,
        description="Complete broker URL (e.g., amqp://user:pass@host:port/vhost)",
    )
    broker_host: str = Field(
        default="",
        description="Broker host",
    )
    broker_port: int = Field(
        default=0,
        description="Broker port",
    )
    broker_user: str = Field(
        default="admin",
        description="Broker username",
    )
    broker_password: str = Field(
        default="admin",
        description="Broker password",
    )
    broker_vhost: str = Field(
        default="/",
        description="Virtual host for broker (RabbitMQ)",
    )
    # broker_type: str = Field(
    #     default="",
    #     description="Tipo do broker: rabbitmq, redis, kafka",
    # )

    # ==================================================================================
    # CELERY SETTINGS
    # ==================================================================================
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Backend for storing task results",
    )
    celery_timezone: str = Field(
        default="UTC",
        description="Timezone for task scheduling",
    )
    celery_task_serializer: str = Field(
        default="json",
        description="Serialization format for sending tasks",
    )
    celery_result_serializer: str = Field(
        default="json",
        description="Serialization format for task results",
    )
    celery_accept_content: list[str] = Field(
        default=["json"],
        description="Accepted content formats in messages",
    )
    celery_task_track_started: bool = Field(
        default=True,
        description="Track when a task starts executing",
    )
    celery_task_time_limit: int = Field(
        default=3600,
        description="Maximum time a task can execute (seconds)",
    )
    celery_task_soft_time_limit: int = Field(
        default=3300,
        description="Soft time limit for graceful cleanup before hard limit",
    )
    celery_worker_prefetch_multiplier: int = Field(
        default=1,
        description="How many tasks a worker can prefetch simultaneously",
    )
    celery_worker_max_tasks_per_child: int = Field(
        default=1000,
        description="Maximum tasks per worker process before restart",
    )

    # ==================================================================================
    # REDIS SETTINGS
    # Suporta URL completa OU variáveis separadas (URL tem prioridade)
    # ==================================================================================
    redis_url: str | None = Field(
        default=None,
        alias="REDIS_URL",
        description="Complete Redis URL (e.g., redis://:password@host:port/db)",
    )
    redis_host: str = Field(
        default="localhost",
        alias="REDIS_HOST",
        description="Redis server host",
    )
    redis_port: int = Field(
        default=6379,
        alias="REDIS_PORT",
        description="Redis server port",
    )
    redis_db: int = Field(
        default=0,
        alias="REDIS_DB",
        description="Redis database number",
    )
    redis_password: str | None = Field(
        default=None,
        alias="REDIS_PASSWORD",
        description="Redis password (optional)",
    )

    # ==================================================================================
    # DJANGO SECURITY SETTINGS
    # ==================================================================================
    secret_key: str = Field(
        default="django-insecure-change-me-in-production",
        description="Django secret key",
    )
    debug: bool = Field(
        default=True,
        description="Debug mode",
    )
    allowed_hosts_raw: str | list[str] = Field(
        default=["*"],
        alias="ALLOWED_HOSTS",
        description="Allowed hosts",
    )

    # ==================================================================================
    # INTERNATIONALIZATION SETTINGS
    # ==================================================================================
    language_code: str = Field(
        default="pt-br",
        description="Language code",
    )
    time_zone: str = Field(
        default="UTC",
        description="Timezone",
    )
    use_i18n: bool = Field(
        default=True,
        description="Use internationalization",
    )
    use_tz: bool = Field(
        default=True,
        description="Use timezone aware",
    )

    # ==================================================================================
    # TEMPLATE SETTINGS
    # ==================================================================================
    template_backend: str = Field(
        default="django.template.backends.django.DjangoTemplates",
        description="Template backend",
    )
    template_dirs: list[str] = Field(
        default_factory=list,
        description="Template directories",
    )
    template_app_dirs: bool = Field(
        default=True,
        description="Search for templates in apps",
    )

    # ==================================================================================
    # APPLICATION SETTINGS
    # ==================================================================================
    api_name: str = Field(
        default="core",
        description="API name",
    )
    default_auto_field: str = Field(
        default="django.db.models.BigAutoField",
        description="Default auto increment field",
    )
    api_group_base_url: str = Field(default="", alias="API_GROUP_BASE_URL")

    # ==================================================================================
    # COMPUTED FIELDS - ALLOWED_HOSTS
    # ==================================================================================
    @computed_field  # type: ignore[prop-decorator]
    @property
    def allowed_hosts(self) -> list[str]:
        """Parse ALLOWED_HOSTS from string to list."""
        if not self.allowed_hosts_raw or str(self.allowed_hosts_raw).strip() == "":
            return ["*"]

        text = str(self.allowed_hosts_raw).strip()

        # Try first to interpret as JSON array
        if text.startswith("[") and text.endswith("]"):
            with suppress(Exception):
                data = json.loads(text)
                if isinstance(data, list):
                    return [str(x).strip() for x in data]

        # Fallback to CSV parsing
        hosts = [h.strip() for h in text.split(",") if h.strip()]
        return hosts or ["*"]

    # ==================================================================================
    # COMPUTED FIELDS - DATABASES
    # ==================================================================================
    @computed_field  # type: ignore[prop-decorator]
    @property
    def databases(self) -> dict[str, dict[str, Any]]:
        """Database configuration in Django format.

        Priority: DATABASE_URL > individual database fields.
        """
        if self.database_url:
            return {"default": self._parse_database_url()}
        return {"default": self._build_database_config()}

    def _parse_database_url(self) -> dict[str, Any]:
        """Parse DATABASE_URL into Django database configuration."""
        parsed = urlparse(self.database_url)
        scheme = str(parsed.scheme).lower()

        # Map scheme to Django engine
        engine_map = {
            "postgresql": "django.db.backends.postgresql",
            "postgres": "django.db.backends.postgresql",
            "mysql": "django.db.backends.mysql",
            "sqlite": "django.db.backends.sqlite3",
        }
        engine = engine_map.get(scheme, f"django.db.backends.{scheme}")

        db_config: dict[str, Any] = {"ENGINE": engine}

        if scheme == "sqlite":
            db_name = str(parsed.path).lstrip("/") if parsed.path else "db.sqlite3"
            db_config["NAME"] = str(
                Path(self.__class__.path_env) / db_name  # type: ignore[attr-defined]
            )
        else:
            # PostgreSQL, MySQL, etc.
            if parsed.path:
                db_config["NAME"] = str(parsed.path).lstrip("/")
            if parsed.username:
                db_config["USER"] = str(parsed.username)
            if parsed.password:
                db_config["PASSWORD"] = str(parsed.password)
            if parsed.hostname:
                db_config["HOST"] = str(parsed.hostname)
            if parsed.port:
                db_config["PORT"] = parsed.port

        return db_config

    def _build_database_config(self) -> dict[str, Any]:
        """Build database configuration from individual fields."""
        db_config: dict[str, Any] = {"ENGINE": self.db_engine}

        if self.db_engine == "django.db.backends.sqlite3":
            db_config["NAME"] = str(
                Path(self.__class__.path_env) / self.db_name  # type: ignore[attr-defined]
            )
        else:
            # PostgreSQL, MySQL, etc.
            if self.db_name:
                db_config["NAME"] = self.db_name
            if self.db_user:
                db_config["USER"] = self.db_user
            if self.db_password:
                db_config["PASSWORD"] = self.db_password
            if self.db_host:
                db_config["HOST"] = self.db_host
            if self.db_port:
                db_config["PORT"] = self.db_port

        return db_config

    # ==================================================================================
    # COMPUTED FIELDS - BROKER
    # ==================================================================================

    @computed_field  # type: ignore[prop-decorator]
    @property
    def broker_type(self) -> str:
        """Return broker type based on URL or host."""
        broker_type = ""
        if self.broker_url:
            parsed = urlparse(self.broker_url)
            scheme = parsed.scheme.lower()
            if scheme in {"amqp", "amqps"}:
                broker_type = "rabbitmq"
            elif scheme == "rediss":
                broker_type = "redis"
            else:
                broker_type = scheme
        elif self.broker_host:
            host_lower = self.broker_host.lower()
            if "rabbit" in host_lower:
                broker_type = "rabbitmq"
            elif "redis" in host_lower:
                broker_type = "redis"
            elif "kafka" in host_lower:
                broker_type = "kafka"
        return broker_type

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_broker_url(self) -> str:
        """Effective broker URL.

        Priority: BROKER_URL > construction from separate variables.
        """
        if self.broker_url:
            return self.broker_url

        # Build URL based on broker type
        if self.broker_type == "rabbitmq":
            # amqp://user:pass@host:port/vhost
            vhost = self.broker_vhost.lstrip("/")
            return f"amqp://{self.broker_user}:{self.broker_password}@{self.broker_host}:{self.broker_port}/{vhost}"
        if self.broker_type == "redis":
            # redis://:pass@host:port/0
            auth = f":{self.broker_password}@" if self.broker_password else ""
            return f"redis://{auth}{self.broker_host}:{self.broker_port}/0"
        if self.broker_type == "kafka":
            # kafka://host:port
            return f"kafka://{self.broker_host}:{self.broker_port}"
        # Generic fallback
        return f"{self.broker_type}://{self.broker_host}:{self.broker_port}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def broker_config(self) -> dict[str, Any]:
        """Complete broker configuration."""
        if self.broker_url:
            parsed = urlparse(self.broker_url)
            return {
                "url": self.broker_url,
                "type": self.broker_type,
                "host": parsed.hostname,
                "port": parsed.port,
            }
        return {
            "url": self.effective_broker_url,
            "type": self.broker_type,
            "host": self.broker_host,
            "port": self.broker_port,
        }

    # ==================================================================================
    # COMPUTED FIELDS - CELERY
    # ==================================================================================
    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_config(self) -> dict[str, Any]:
        """Celery configuration in expected format."""
        return {
            "broker_url": self.effective_broker_url,  # Use effective broker URL
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

    # ==================================================================================
    # COMPUTED FIELDS - REDIS
    # ==================================================================================
    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_redis_url(self) -> str:
        """Effective Redis URL.

        Priority: REDIS_URL > construction from separate variables.
        """
        if self.redis_url:
            return self.redis_url

        # Build URL from separate variables
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_config(self) -> dict[str, Any]:
        """Complete Redis configuration."""
        # If we have URL, parse it
        if self.redis_url:
            parsed = urlparse(self.redis_url)
            return {
                "url": self.redis_url,
                "host": parsed.hostname or self.redis_host,
                "port": parsed.port or self.redis_port,
                "db": int(parsed.path.lstrip("/"))
                if parsed.path and parsed.path.lstrip("/").isdigit()
                else self.redis_db,
                "password": parsed.password or self.redis_password,
            }

        # Otherwise use separate variables
        return {
            "url": self.effective_redis_url,
            "host": self.redis_host,
            "port": self.redis_port,
            "db": self.redis_db,
            "password": self.redis_password,
        }

    # ==================================================================================
    # COMPUTED FIELDS - TEMPLATES
    # ==================================================================================
    @computed_field  # type: ignore[prop-decorator]
    @property
    def templates(self) -> list[dict[str, Any]]:
        """Template configuration in Django format."""
        return [
            {
                "BACKEND": self.template_backend,
                "DIRS": self.template_dirs,
                "APP_DIRS": self.template_app_dirs,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ]

    # ==================================================================================
    # PROPERTY FIELDS - DEFAULTS
    # ==================================================================================
    @property
    def default_installed_apps(self) -> list[str]:
        """Default Django apps."""
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
        """Default Django middleware."""
        return [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]

    @property
    def default_auth_password_validators(self) -> list[dict[str, str]]:
        """Default Django password validators."""
        return [
            {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
            {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
            {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        ]

    @property
    def default_logging(self) -> dict[str, Any]:
        """Default logging configuration."""
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

    @property
    def default_logging_config(self) -> str:
        """Path to logging configuration function."""
        return "logging.config.dictConfig"

    # ==================================================================================
    # UTILITY METHODS
    # ==================================================================================
    def to_dict(self) -> dict[str, Any]:
        """Return Django configuration as a dictionary."""
        result = {}
        for key in DJANGO_SETTINGS_KEYS:
            value = getattr(self, key.lower(), None)
            if value is not None:
                result[key] = value
        return result
