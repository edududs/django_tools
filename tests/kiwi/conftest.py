"""Shared pytest fixtures and configuration for django_tools tests."""

from unittest.mock import Mock

import pytest
from dependency_injector import providers
from django_tools.kiwi.celery import _CeleryAppSingleton

from django_tools.kiwi import KiwiContainer
from django_tools.settings import DjangoSettingsBaseModel


@pytest.fixture(autouse=True)
def reset_celery_singleton():
    """Reset Celery singleton before and after each test to ensure isolation."""
    _CeleryAppSingleton.reset()
    yield
    _CeleryAppSingleton.reset()


@pytest.fixture
def container():
    """Provide a fresh KiwiContainer instance for testing."""
    return KiwiContainer()


@pytest.fixture
def mock_settings():
    """Provide a mocked DjangoSettings instance with test configuration.

    This fixture creates a mock that simulates DjangoSettings behavior
    without requiring actual environment variables or .env files.
    """
    settings = Mock(spec=DjangoSettingsBaseModel)
    settings.effective_broker_url = "redis://localhost:6379/0"
    settings.celery_result_backend = "redis://localhost:6379/1"
    settings.celery_timezone = "UTC"
    settings.celery_task_serializer = "json"
    settings.celery_result_serializer = "json"
    settings.celery_accept_content = ["json"]
    settings.celery_task_track_started = True
    settings.celery_task_time_limit = 3600
    settings.celery_task_soft_time_limit = 3300
    settings.celery_worker_prefetch_multiplier = 1
    settings.celery_worker_max_tasks_per_child = 1000
    return settings


@pytest.fixture
def mocked_container(mock_settings):
    """Provide a KiwiContainer with mocked configuration.

    This fixture creates a container where the configuration is overridden
    with mocked settings, allowing isolated testing of Celery configuration
    without depending on actual Django settings.
    """
    container = KiwiContainer()
    container.config.override(providers.Configuration(pydantic_settings=[mock_settings]))
    return container


@pytest.fixture
def alternative_mock_settings():
    """Provide an alternative mocked DjangoSettings for testing overrides."""
    settings = Mock(spec=DjangoSettingsBaseModel)
    settings.effective_broker_url = "amqp://guest:guest@localhost:5672//"
    settings.celery_result_backend = "rpc://"
    settings.celery_timezone = "America/Sao_Paulo"
    settings.celery_task_serializer = "json"
    settings.celery_result_serializer = "json"
    settings.celery_accept_content = ["json", "pickle"]
    settings.celery_task_track_started = False
    settings.celery_task_time_limit = 7200
    settings.celery_task_soft_time_limit = 6600
    settings.celery_worker_prefetch_multiplier = 4
    settings.celery_worker_max_tasks_per_child = 500
    return settings
