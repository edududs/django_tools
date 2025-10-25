"""Tests for the settings system."""

from pathlib import Path

from django_tools.settings import Settings
from django_tools.settings.base.infra.settings_celery import CelerySettings
from django_tools.settings.base.infra.settings_database import DatabaseSettings
from django_tools.settings.base.infra.settings_rabbit import RabbitMQSettings
from django_tools.settings.base.infra.settings_redis import RedisSettings
from django_tools.settings.base.settings_django import DjangoSettingsBaseModel


class TestDjangoSettings:
    """Tests for DjangoSettingsBaseModel."""

    def test_load_from_env_file(self, tmp_env_django: Path):
        """Loads Django settings from .env file."""
        settings = DjangoSettingsBaseModel(_env_file=str(tmp_env_django))

        assert settings.secret_key == "django-test-secret"
        assert settings.debug is True
        assert settings.allowed_hosts == ["app.example.com", "api.example.com"]
        assert settings.language_code == "en-us"
        assert settings.time_zone == "UTC"
        assert settings.api_name == "django-app"

    def test_allowed_hosts_parsing_json(self, tmp_path: Path):
        """Tests parsing ALLOWED_HOSTS in JSON format."""
        env_file = tmp_path / ".env"
        env_file.write_text('ALLOWED_HOSTS=["host1.com","host2.com"]')

        settings = DjangoSettingsBaseModel(_env_file=str(env_file))

        assert settings.allowed_hosts == ["host1.com", "host2.com"]

    def test_allowed_hosts_parsing_direct_list(self, tmp_path: Path):
        """Tests parsing ALLOWED_HOSTS passing list directly via env."""
        env_file = tmp_path / ".env"
        env_file.write_text('ALLOWED_HOSTS=["direct","list"]')

        settings = DjangoSettingsBaseModel(_env_file=str(env_file))

        assert settings.allowed_hosts == ["direct", "list"]

    def test_allowed_hosts_parsing_empty(self):
        """Tests that empty ALLOWED_HOSTS returns default."""
        settings = DjangoSettingsBaseModel(allowed_hosts="")

        assert settings.allowed_hosts == ["*"]

    def test_defaults(self):
        """Checks default values for Django settings."""
        settings = DjangoSettingsBaseModel()

        assert settings.secret_key == "django-insecure-change-me-in-production"
        assert settings.debug is True
        assert settings.allowed_hosts == ["*"]
        assert settings.language_code == "pt-br"
        assert settings.time_zone == "UTC"
        assert settings.use_i18n is True
        assert settings.use_tz is True
        assert settings.api_name == "core"

    def test_validation_alias(self, tmp_path: Path):
        """Tests validation aliases (SECRET_KEY vs DJANGO_SECRET_KEY)."""
        env_file = tmp_path / ".env"
        env_file.write_text('DJANGO_SECRET_KEY="alias-secret"')

        settings = DjangoSettingsBaseModel(_env_file=str(env_file))

        assert settings.secret_key == "alias-secret"


class TestDatabaseSettings:
    """Tests for DatabaseSettings."""

    def test_load_from_url(self, tmp_env_database: Path):
        """Loads settings via DATABASE_URL."""
        settings = DatabaseSettings(_env_file=str(tmp_env_database))

        assert settings.url == "postgresql://dbuser:dbpass@db.example.com:5432/production"
        assert settings.conn_max_age == 600
        assert settings.conn_health_checks is True
        assert settings.time_zone == "UTC"

    def test_load_from_fields(self, tmp_env_database_fields: Path):
        """Loads settings via individual fields."""
        settings = DatabaseSettings(_env_file=str(tmp_env_database_fields))

        assert settings.engine == "django.db.backends.mysql"
        assert settings.name == "mydb"
        assert settings.user == "myuser"
        assert settings.password == "mypass"
        assert settings.host == "mysql.example.com"
        assert settings.port == 3306

    def test_alias_choices(self, tmp_path: Path):
        """Tests DATABASE_* vs DB_* aliases."""
        env_file = tmp_path / ".env"
        env_file.write_text('DB_NAME="aliasdb"\nDB_USER="aliasuser"')

        settings = DatabaseSettings(_env_file=str(env_file))

        assert settings.name == "aliasdb"
        assert settings.user == "aliasuser"

    def test_defaults(self):
        """Checks default values for database settings."""
        settings = DatabaseSettings()

        assert settings.url is None
        assert settings.engine == "django.db.backends.sqlite3"
        assert settings.name == "db.sqlite3"
        assert settings.user is None
        assert settings.password is None
        assert settings.host is None
        assert settings.port is None
        assert settings.autocommit is True
        assert settings.atomic_requests is False
        assert settings.conn_max_age == 0


class TestCelerySettings:
    """Tests for CelerySettings."""

    def test_load_from_env(self, tmp_env_celery: Path):
        """Loads Celery settings from .env."""
        settings = CelerySettings(_env_file=str(tmp_env_celery))

        assert settings.broker_url == "redis://localhost:6379/0"
        assert settings.result_backend == "redis://localhost:6379/1"
        assert settings.timezone == "America/New_York"
        assert settings.task_serializer == "pickle"
        assert settings.task_compression == "bzip2"
        assert settings.worker_concurrency == 8
        assert settings.worker_pool == "threads"

    def test_json_fields(self, tmp_env_celery: Path):
        """Tests JSON fields (task_queues, task_routes, beat_schedule)."""
        settings = CelerySettings(_env_file=str(tmp_env_celery))

        assert settings.task_queues == [
            {"name": "high", "routing_key": "high"},
            {"name": "low", "routing_key": "low"},
        ]
        assert settings.task_routes == {"app.tasks.urgent": {"queue": "high"}}
        assert settings.beat_schedule == {"task1": {"task": "app.tasks.periodic", "schedule": 30.0}}

    def test_defaults(self):
        """Checks default values for Celery settings."""
        settings = CelerySettings()

        assert settings.broker_url is None
        assert settings.result_backend is None
        assert settings.timezone == "UTC"
        assert settings.enable_utc is True
        assert settings.accept_content == ["json"]
        assert settings.task_serializer == "json"
        assert settings.task_compression is None
        assert settings.task_default_queue == "default"
        assert settings.worker_prefetch_multiplier == 1
        assert settings.worker_max_tasks_per_child == 1000


class TestRedisSettings:
    """Tests for RedisSettings."""

    def test_url_to_fields_conversion(self, tmp_env_redis: Path):
        """Tests conversion from REDIS_URL to individual fields."""
        settings = RedisSettings(_env_file=str(tmp_env_redis))

        assert settings.url == "redis://:secretpass@redis.prod.com:6380/5"
        assert settings.host == "redis.prod.com"
        assert settings.port == 6380
        assert settings.db == 5
        assert settings.password == "secretpass"

    def test_fields_to_url_conversion(self, tmp_env_redis_fields: Path):
        """Tests conversion from individual fields to URL."""
        settings = RedisSettings(_env_file=str(tmp_env_redis_fields))

        assert settings.host == "redis.example.com"
        assert settings.port == 6380
        assert settings.db == 3
        assert settings.password == "redispass"
        assert settings.url == "redis://:redispass@redis.example.com:6380/3"

    def test_load_from_url_only(self, tmp_path: Path):
        """Loads only via REDIS_URL."""
        env_file = tmp_path / ".env"
        env_file.write_text('REDIS_URL="redis://:pass123@localhost:6379/1"')

        settings = RedisSettings(_env_file=str(env_file))

        assert settings.url == "redis://:pass123@localhost:6379/1"
        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.db == 1
        assert settings.password == "pass123"

    def test_load_from_fields_only(self, tmp_path: Path):
        """Loads only via individual fields."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            'REDIS_HOST="myredis.com"\nREDIS_PORT=6380\nREDIS_DB=2\nREDIS_PASSWORD="mypass"'
        )

        settings = RedisSettings(_env_file=str(env_file))

        assert settings.host == "myredis.com"
        assert settings.port == 6380
        assert settings.db == 2
        assert settings.password == "mypass"
        assert settings.url == "redis://:mypass@myredis.com:6380/2"

    def test_defaults(self):
        """Checks default values for Redis settings."""
        settings = RedisSettings()

        assert settings.url is None
        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.db == 0
        assert settings.password is None


class TestRabbitMQSettings:
    """Tests for RabbitMQSettings."""

    def test_url_to_fields_conversion(self, tmp_env_rabbit: Path):
        """Tests conversion from RABBIT_URL to individual fields."""
        settings = RabbitMQSettings(_env_file=str(tmp_env_rabbit))

        assert settings.url == "amqp://rabbituser:rabbitpass@rabbit.prod.com:5673/production"
        assert settings.host == "rabbit.prod.com"
        assert settings.port == 5673
        assert settings.vhost == "/production"
        assert settings.username == "rabbituser"
        assert settings.password == "rabbitpass"

    def test_fields_to_url_conversion(self, tmp_env_rabbit_fields: Path):
        """Tests conversion from individual fields to URL."""
        settings = RabbitMQSettings(_env_file=str(tmp_env_rabbit_fields))

        assert settings.host == "rabbit.example.com"
        assert settings.port == 5673
        assert settings.vhost == "/myapp"
        assert settings.username == "rabbituser"
        assert settings.password == "rabbitpass"
        assert settings.url == "amqp://rabbituser:rabbitpass@rabbit.example.com:5673/myapp"

    def test_load_from_url_only(self, tmp_path: Path):
        """Loads only via RABBIT_URL."""
        env_file = tmp_path / ".env"
        env_file.write_text('RABBIT_URL="amqp://user:pass@localhost:5672/vhost"')

        settings = RabbitMQSettings(_env_file=str(env_file))

        assert settings.url == "amqp://user:pass@localhost:5672/vhost"
        assert settings.host == "localhost"
        assert settings.port == 5672
        assert settings.vhost == "/vhost"
        assert settings.username == "user"
        assert settings.password == "pass"

    def test_load_from_fields_only(self, tmp_path: Path):
        """Loads only via individual fields."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            'RABBIT_HOST="myrabbit.com"\n'
            "RABBIT_PORT=5673\n"
            'RABBIT_VHOST="/app"\n'
            'RABBIT_USERNAME="myuser"\n'
            'RABBIT_PASSWORD="mypass"'
        )

        settings = RabbitMQSettings(_env_file=str(env_file))

        assert settings.host == "myrabbit.com"
        assert settings.port == 5673
        assert settings.vhost == "/app"
        assert settings.username == "myuser"
        assert settings.password == "mypass"
        assert settings.url == "amqp://myuser:mypass@myrabbit.com:5673/app"

    def test_defaults(self):
        """Checks default values for RabbitMQ settings."""
        settings = RabbitMQSettings()

        assert settings.url is None
        assert settings.host == "localhost"
        assert settings.port == 5672
        assert settings.vhost == "/"
        assert settings.username == "guest"
        assert settings.password == "guest"


class TestSettingsContainer:
    """Tests for the main Settings class."""

    def test_load_all_settings(self, tmp_env_file: Path):
        """Tests loading all settings."""
        settings = Settings(env_file=str(tmp_env_file))

        # Django
        assert settings.dj.secret_key == "test-secret-key-12345"
        assert settings.dj.debug is False
        assert settings.dj.time_zone == "America/Sao_Paulo"

        # Database
        assert settings.db.url == "postgresql://testuser:testpass@localhost:5432/testdb"
        assert settings.db.engine == "django.db.backends.postgresql"

        # Celery
        assert settings.celery.broker_url == "amqp://guest:guest@localhost:5672/"
        assert settings.celery.result_backend == "redis://localhost:6379/1"

        # Redis
        assert settings.redis.url == "redis://:mypassword@redis.example.com:6379/2"
        assert settings.redis.host == "redis.example.com"

        # RabbitMQ
        assert settings.rabbit.url == "amqp://admin:admin123@rabbitmq.example.com:5672/myapp"
        assert settings.rabbit.host == "rabbitmq.example.com"

    def test_model_dump(self, tmp_env_minimal: Path):
        """Tests serialization via model_dump."""
        settings = Settings(env_file=str(tmp_env_minimal))
        data = settings.model_dump()

        assert isinstance(data, dict)
        assert "SECRET_KEY" in data
        assert data["SECRET_KEY"] == "minimal-secret"
        assert "CELERY_BROKER_URL" in data
        assert "REDIS_URL" in data

    def test_str_representation(self, tmp_env_minimal: Path):
        """Tests string representation of the Settings class."""
        settings = Settings(env_file=str(tmp_env_minimal))
        str_repr = str(settings)

        assert "DJANGO SETTINGS:" in str_repr
        assert "CELERY SETTINGS:" in str_repr
        assert "DATABASE SETTINGS:" in str_repr
        assert "RABBITMQ SETTINGS:" in str_repr
        assert "REDIS SETTINGS:" in str_repr

    def test_individual_components_accessible(self, tmp_env_file: Path):
        """Tests individual access to settings' components."""
        settings = Settings(env_file=str(tmp_env_file))

        assert isinstance(settings.dj, DjangoSettingsBaseModel)
        assert isinstance(settings.db, DatabaseSettings)
        assert isinstance(settings.celery, CelerySettings)
        assert isinstance(settings.redis, RedisSettings)
        assert isinstance(settings.rabbit, RabbitMQSettings)
