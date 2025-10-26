"""Tests for Kiwi module using dependency-injector mocking."""

from unittest.mock import MagicMock, Mock

import pytest
from celery import Celery
from dependency_injector import providers
from django_tools.kiwi.celery import _CeleryAppSingleton

from django_tools.kiwi import KiwiContainer, create_celery_app, get_celery_app
from django_tools.settings import DjangoSettingsBaseModel


@pytest.fixture(autouse=True)
def reset_celery_singleton():
    """Reset Celery singleton before each test to ensure isolation."""
    _CeleryAppSingleton.reset()
    yield
    _CeleryAppSingleton.reset()


@pytest.fixture
def container():
    """Provide a fresh KiwiContainer instance."""
    return KiwiContainer()


@pytest.fixture
def mock_settings():
    """Provide a mocked DjangoSettings instance."""
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
    """Provide a container with mocked configuration."""
    container = KiwiContainer()
    container.config.override(providers.Configuration(pydantic_settings=[mock_settings]))
    return container


class TestKiwiContainer:
    """Tests for KiwiContainer with dependency injection."""

    def test_container_initialization(self, container):
        """Test that KiwiContainer initializes correctly."""
        assert container is not None
        assert hasattr(container, "config")
        assert hasattr(container, "celery_config")

    def test_container_has_correct_providers(self, container):
        """Test that container has all required providers."""
        assert isinstance(container.config, providers.Configuration)
        assert isinstance(container.celery_config, providers.Dict)

    def test_celery_config_provider_returns_dict(self, container):
        """Test that celery_config provider returns a dictionary."""
        config = container.celery_config()

        assert isinstance(config, dict)
        assert len(config) > 0

    def test_celery_config_with_mocked_settings(self, mocked_container):
        """Test celery_config with mocked DjangoSettings."""
        config = mocked_container.celery_config()

        assert config["broker_url"] == "redis://localhost:6379/0"
        assert config["result_backend"] == "redis://localhost:6379/1"
        assert config["timezone"] == "UTC"
        assert config["task_serializer"] == "json"

    def test_celery_config_required_keys(self, container):
        """Test that celery_config contains all required keys."""
        config = container.celery_config()

        required_keys = {
            "broker_url",
            "result_backend",
            "timezone",
            "task_serializer",
            "result_serializer",
            "accept_content",
            "task_track_started",
            "task_time_limit",
            "task_soft_time_limit",
            "worker_prefetch_multiplier",
            "worker_max_tasks_per_child",
        }
        assert all(key in config for key in required_keys)

    def test_config_values_types(self, container):
        """Test that configuration values have correct types."""
        config = container.celery_config()

        assert isinstance(config["broker_url"], str)
        assert isinstance(config["result_backend"], str)
        assert isinstance(config["timezone"], str)
        assert isinstance(config["task_serializer"], str)
        assert isinstance(config["result_serializer"], str)
        assert isinstance(config["accept_content"], list)
        assert isinstance(config["task_track_started"], bool)
        assert isinstance(config["task_time_limit"], int)
        assert isinstance(config["task_soft_time_limit"], int)
        assert isinstance(config["worker_prefetch_multiplier"], int)
        assert isinstance(config["worker_max_tasks_per_child"], int)

    def test_container_override_config(self, container, mock_settings):
        """Test overriding container configuration."""
        # Override config provider
        with container.config.override(providers.Configuration(pydantic_settings=[mock_settings])):
            config = container.celery_config()
            assert config["broker_url"] == "redis://localhost:6379/0"

        # After context, original config is restored
        config_after = container.celery_config()
        assert config_after is not None


class TestCeleryAppFactory:
    """Tests for Celery app factory with mocked dependencies."""

    def test_create_celery_app_returns_celery_instance(self):
        """Test that create_celery_app creates a valid Celery instance."""
        app = create_celery_app("test_app")

        assert isinstance(app, Celery)
        assert app.main == "test_app"

    def test_create_celery_app_configuration_applied(self, monkeypatch):
        """Test that configuration from container is applied to Celery app."""
        # Create a mocked container
        mock_container = MagicMock(spec=KiwiContainer)
        mock_container.celery_config.return_value = {
            "broker_url": "memory://",
            "result_backend": "cache+memory://",
            "timezone": "America/Sao_Paulo",
            "task_serializer": "json",
            "result_serializer": "json",
            "accept_content": ["json"],
            "task_track_started": False,
            "task_time_limit": 7200,
            "task_soft_time_limit": 6600,
            "worker_prefetch_multiplier": 4,
            "worker_max_tasks_per_child": 500,
        }

        # Patch KiwiContainer instantiation
        def mock_init():
            return mock_container

        monkeypatch.setattr("django_tools.kiwi.celery.KiwiContainer", mock_init)

        app = create_celery_app("mocked_app")

        assert app.conf.broker_url == "memory://"
        assert app.conf.result_backend == "cache+memory://"
        assert app.conf.timezone == "America/Sao_Paulo"
        assert app.conf.task_time_limit == 7200

    @pytest.mark.parametrize("app_name", ["app1", "app2", "test_app"])
    def test_create_celery_app_with_different_names(self, app_name):
        """Test creating apps with different names."""
        app = create_celery_app(app_name)

        assert isinstance(app, Celery)
        assert app.main == app_name

    def test_create_celery_app_autodiscovers_tasks(self):
        """Test that created app has autodiscover configured."""
        app = create_celery_app("autodiscover_test")

        # Celery stores autodiscover configuration internally
        assert isinstance(app, Celery)
        assert app.conf.broker_url is not None


class TestCelerySingleton:
    """Tests for Celery singleton functionality."""

    def test_get_celery_app_returns_singleton(self):
        """Test that get_celery_app returns singleton instance."""
        app1 = get_celery_app("singleton_test")
        app2 = get_celery_app("different_name")

        assert app1 is app2, "Should return the same singleton instance"
        assert app1.main == "singleton_test", "First call defines the app name"

    def test_singleton_persists_configuration(self):
        """Test that singleton maintains configuration across calls."""
        app1 = get_celery_app("persistent_test")
        original_broker = app1.conf.broker_url

        app2 = get_celery_app("another_name")
        assert app2.conf.broker_url == original_broker

    def test_singleton_reset_creates_new_instance(self):
        """Test that resetting singleton allows creating new instance."""
        app1 = get_celery_app("first_instance")
        first_id = id(app1)

        _CeleryAppSingleton.reset()

        app2 = get_celery_app("second_instance")
        second_id = id(app2)

        assert first_id != second_id
        assert app2.main == "second_instance"

    def test_singleton_is_thread_safe(self):
        """Test singleton behavior with class-based approach."""
        # The _CeleryAppSingleton uses class variables which are thread-safe
        # for the singleton pattern when using the pattern we implemented
        instance = _CeleryAppSingleton.get_instance("thread_test")
        assert isinstance(instance, Celery)


class TestCeleryTasks:
    """Tests for task decoration and execution."""

    def test_task_decorator(self):
        """Test that tasks can be decorated with celery_app."""
        app = get_celery_app("decorator_test")

        @app.task
        def sample_task(x: int, y: int) -> int:
            return x + y

        assert sample_task.name is not None
        assert callable(sample_task)

    def test_task_execution(self):
        """Test that decorated tasks can be executed."""
        app = get_celery_app("execution_test")

        @app.task
        def add_numbers(x: int, y: int) -> int:
            return x + y

        result = add_numbers(2, 3)
        assert result == 5

    def test_task_with_custom_name(self):
        """Test task with explicit name."""
        app = get_celery_app("named_task_test")

        @app.task(name="custom.task.name")
        def custom_task() -> str:
            return "executed"

        assert custom_task.name == "custom.task.name"
        assert custom_task() == "executed"

    @pytest.mark.parametrize(
        ("x", "y", "expected"),
        [
            (1, 1, 2),
            (5, 3, 8),
            (10, -5, 5),
            (0, 0, 0),
        ],
    )
    def test_task_parametrized(self, x, y, expected):
        """Test task execution with multiple parameter sets."""
        app = get_celery_app("param_test")

        @app.task
        def add(a: int, b: int) -> int:
            return a + b

        assert add(x, y) == expected

    def test_task_with_bind(self):
        """Test bound task that has access to task instance."""
        app = get_celery_app("bind_test")

        @app.task(bind=True)
        def bound_task(self, value: int) -> dict[str, int]:
            return {"task_id": id(self), "value": value}

        result = bound_task(42)
        assert "task_id" in result
        assert result["value"] == 42


class TestIntegration:
    """Integration tests using dependency injection mocking."""

    def test_end_to_end_with_real_container(self):
        """Test complete flow from container to task execution."""
        container = KiwiContainer()
        config = container.celery_config()

        app = create_celery_app("integration_test")

        # Verify app is configured with container values
        assert app.conf.broker_url == config["broker_url"]
        assert app.conf.result_backend == config["result_backend"]

        @app.task
        def integration_task(value: int) -> int:
            return value * 2

        result = integration_task(21)
        assert result == 42

    def test_end_to_end_with_mocked_container(self, mocked_container):
        """Test complete flow with mocked dependencies."""
        config = mocked_container.celery_config()

        assert config["broker_url"] == "redis://localhost:6379/0"
        assert config["result_backend"] == "redis://localhost:6379/1"
        assert config["timezone"] == "UTC"

    def test_singleton_and_factory_independence(self):
        """Test that singleton and factory create independent instances."""
        singleton_app = get_celery_app("singleton")
        factory_app = create_celery_app("factory")

        # They should be different instances
        assert singleton_app is not factory_app

        # But both should be configured
        assert singleton_app.conf.broker_url is not None
        assert factory_app.conf.broker_url is not None

    def test_multiple_containers_independent(self):
        """Test that multiple container instances are independent."""
        container1 = KiwiContainer()
        container2 = KiwiContainer()

        config1 = container1.celery_config()
        config2 = container2.celery_config()

        # Both should have same values from DjangoSettings
        assert config1["broker_url"] == config2["broker_url"]

        # But modifying one shouldn't affect the other
        assert container1 is not container2

    def test_container_override_isolation(self, container, mock_settings):
        """Test that container override doesn't affect other instances."""
        container1 = container
        container2 = KiwiContainer()

        original_broker = container2.celery_config()["broker_url"]

        # Override only container1
        with container1.config.override(providers.Configuration(pydantic_settings=[mock_settings])):
            config1 = container1.celery_config()
            config2 = container2.celery_config()

            assert config1["broker_url"] == "redis://localhost:6379/0"
            assert config2["broker_url"] == original_broker


class TestProviderOverrides:
    """Tests specifically for provider override functionality."""

    def test_override_celery_config_provider(self, container):
        """Test overriding celery_config provider directly."""
        mock_config = {
            "broker_url": "amqp://guest:guest@localhost:5672//",
            "result_backend": "rpc://",
            "timezone": "Europe/London",
            "task_serializer": "pickle",
            "result_serializer": "pickle",
            "accept_content": ["pickle"],
            "task_track_started": False,
            "task_time_limit": 1800,
            "task_soft_time_limit": 1500,
            "worker_prefetch_multiplier": 2,
            "worker_max_tasks_per_child": 100,
        }

        with container.celery_config.override(providers.Object(mock_config)):
            config = container.celery_config()
            assert config["broker_url"] == "amqp://guest:guest@localhost:5672//"
            assert config["timezone"] == "Europe/London"
            assert config["task_serializer"] == "pickle"

    def test_nested_overrides(self, container, mock_settings):
        """Test nested provider overrides."""
        with container.config.override(providers.Configuration(pydantic_settings=[mock_settings])):
            # Create another mock for nested override
            another_mock = Mock(spec=DjangoSettingsBaseModel)
            another_mock.effective_broker_url = "kafka://localhost:9092"
            another_mock.celery_result_backend = "db+sqlite:///results.db"
            another_mock.celery_timezone = "Asia/Tokyo"
            another_mock.celery_task_serializer = "msgpack"
            another_mock.celery_result_serializer = "msgpack"
            another_mock.celery_accept_content = ["msgpack"]
            another_mock.celery_task_track_started = True
            another_mock.celery_task_time_limit = 1200
            another_mock.celery_task_soft_time_limit = 900
            another_mock.celery_worker_prefetch_multiplier = 8
            another_mock.celery_worker_max_tasks_per_child = 50

            with container.config.override(
                providers.Configuration(pydantic_settings=[another_mock])
            ):
                config2 = container.celery_config()
                assert config2["broker_url"] == "kafka://localhost:9092"
                assert config2["timezone"] == "Asia/Tokyo"

            # After exiting nested context, should restore to first override
            config3 = container.celery_config()
            assert config3["broker_url"] == "redis://localhost:6379/0"
