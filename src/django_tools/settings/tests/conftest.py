"""Fixtures para testes de settings."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_env_file(tmp_path: Path) -> Path:
    """Cria arquivo .env temporário com configurações completas."""
    env_file = tmp_path / ".env"
    content = """
SECRET_KEY="test-secret-key-12345"
DEBUG=false
ALLOWED_HOSTS=["localhost","127.0.0.1","test.com"]
LANGUAGE_CODE="pt-br"
TIME_ZONE="America/Sao_Paulo"
API_NAME="test-api"

DATABASE_URL="postgresql://testuser:testpass@localhost:5432/testdb"
DATABASE_ENGINE="django.db.backends.postgresql"
DATABASE_NAME="testdb"
DATABASE_USER="testuser"
DATABASE_PASSWORD="testpass"
DATABASE_HOST="localhost"
DATABASE_PORT=5432
DATABASE_CONN_MAX_AGE=300
DATABASE_CONN_HEALTH_CHECKS=true

CELERY_BROKER_URL="amqp://guest:guest@localhost:5672/"
CELERY_RESULT_BACKEND="redis://localhost:6379/1"
CELERY_TIMEZONE="America/Sao_Paulo"
CELERY_ACCEPT_CONTENT=["json","pickle"]
CELERY_TASK_SERIALIZER="json"
CELERY_TASK_COMPRESSION="gzip"
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_POOL="prefork"

REDIS_URL="redis://:mypassword@redis.example.com:6379/2"
RABBIT_URL="amqp://admin:admin123@rabbitmq.example.com:5672/myapp"
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_minimal(tmp_path: Path) -> Path:
    """Cria arquivo .env temporário com configurações mínimas."""
    env_file = tmp_path / ".env"
    content = """
SECRET_KEY="minimal-secret"
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_django(tmp_path: Path) -> Path:
    """Cria arquivo .env focado em Django settings."""
    env_file = tmp_path / ".env"
    content = """
SECRET_KEY="django-test-secret"
DEBUG=true
ALLOWED_HOSTS=["app.example.com","api.example.com"]
LANGUAGE_CODE="en-us"
TIME_ZONE="UTC"
USE_I18N=true
USE_TZ=true
API_NAME="django-app"
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_database(tmp_path: Path) -> Path:
    """Cria arquivo .env focado em Database settings."""
    env_file = tmp_path / ".env"
    content = """
DATABASE_URL="postgresql://dbuser:dbpass@db.example.com:5432/production"
DATABASE_CONN_MAX_AGE=600
DATABASE_CONN_HEALTH_CHECKS=true
DATABASE_TIME_ZONE="UTC"
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_database_fields(tmp_path: Path) -> Path:
    """Cria arquivo .env com campos individuais de database."""
    env_file = tmp_path / ".env"
    content = """
DB_ENGINE="django.db.backends.mysql"
DB_NAME="mydb"
DB_USER="myuser"
DB_PASSWORD="mypass"
DB_HOST="mysql.example.com"
DB_PORT=3306
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_celery(tmp_path: Path) -> Path:
    """Cria arquivo .env focado em Celery settings."""
    env_file = tmp_path / ".env"
    content = """
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/1"
CELERY_TIMEZONE="America/New_York"
CELERY_TASK_SERIALIZER="pickle"
CELERY_TASK_COMPRESSION="bzip2"
CELERY_WORKER_CONCURRENCY=8
CELERY_WORKER_POOL="threads"
CELERY_TASK_QUEUES=[{"name":"high","routing_key":"high"},{"name":"low","routing_key":"low"}]
CELERY_TASK_ROUTES={"app.tasks.urgent":{"queue":"high"}}
CELERY_BEAT_SCHEDULE={"task1":{"task":"app.tasks.periodic","schedule":30.0}}
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_redis(tmp_path: Path) -> Path:
    """Cria arquivo .env focado em Redis settings com URL."""
    env_file = tmp_path / ".env"
    content = """
REDIS_URL="redis://:secretpass@redis.prod.com:6380/5"
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_redis_fields(tmp_path: Path) -> Path:
    """Cria arquivo .env focado em Redis settings com campos individuais."""
    env_file = tmp_path / ".env"
    content = """
REDIS_HOST="redis.example.com"
REDIS_PORT=6380
REDIS_DB=3
REDIS_PASSWORD="redispass"
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_rabbit(tmp_path: Path) -> Path:
    """Cria arquivo .env focado em RabbitMQ settings com URL."""
    env_file = tmp_path / ".env"
    content = """
RABBIT_URL="amqp://rabbituser:rabbitpass@rabbit.prod.com:5673/production"
"""
    env_file.write_text(content.strip())
    return env_file


@pytest.fixture
def tmp_env_rabbit_fields(tmp_path: Path) -> Path:
    """Cria arquivo .env focado em RabbitMQ settings com campos individuais."""
    env_file = tmp_path / ".env"
    content = """
RABBIT_HOST="rabbit.example.com"
RABBIT_PORT=5673
RABBIT_VHOST="/myapp"
RABBIT_USERNAME="rabbituser"
RABBIT_PASSWORD="rabbitpass"
"""
    env_file.write_text(content.strip())
    return env_file
