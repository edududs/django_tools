# Testing with Dependency Injector

Comprehensive testing guide for `django_tools` using pytest and dependency-injector's powerful mocking capabilities.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Understanding Dependency Injection in Tests](#understanding-dependency-injection-in-tests)
- [Testing Strategies](#testing-strategies)
- [Available Fixtures](#available-fixtures)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

This test suite leverages **dependency-injector** for true dependency injection testing. Instead of traditional mocking with `unittest.mock`, we use provider overrides to inject test dependencies cleanly and pythonically.

### Why Dependency Injection for Testing?

- **True Isolation**: Replace dependencies at the container level, not at the module level
- **No Monkey Patching**: Clean, explicit dependency replacement
- **Type Safety**: Maintains type hints and IDE support
- **Reusability**: Shared fixtures for common test configurations
- **Composability**: Nest and combine overrides easily

## Test Structure

```text
tests/
├── __init__.py
├── conftest.py          # Shared pytest fixtures
├── test_kiwi.py         # Kiwi module tests with DI patterns
└── README.md            # This file
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_kiwi.py

# Run specific test class
pytest tests/test_kiwi.py::TestKiwiContainer

# Run specific test
pytest tests/test_kiwi.py::TestKiwiContainer::test_container_initialization
```

### With Coverage

```bash
# Generate HTML coverage report
pytest --cov=django_tools --cov-report=html

# Terminal report with missing lines
pytest --cov=django_tools.kiwi --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Advanced Options

```bash
# Verbose output
pytest -v

# Extra verbose (show test docstrings)
pytest -vv

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

## Understanding Dependency Injection in Tests

### Core Concepts

#### 1. Containers

Containers hold providers and manage dependencies:

```python
from django_tools.kiwi import KiwiContainer

container = KiwiContainer()
config = container.celery_config()  # Get dependency
```

#### 2. Providers

Providers define how dependencies are created:

- `providers.Configuration`: Settings and configuration
- `providers.Dict`: Dictionary-based configuration
- `providers.Factory`: Creates new instance each time
- `providers.Singleton`: Single instance, reused
- `providers.Object`: Wraps existing object

#### 3. Provider Overrides

Replace providers for testing:

```python
# Override a single provider
with container.celery_config.override(providers.Object(mock_config)):
    config = container.celery_config()  # Returns mock_config

# Override Configuration provider
with container.config.override(
    providers.Configuration(pydantic_settings=[mock_settings])
):
    config = container.celery_config()  # Uses mock_settings
```

## Testing Strategies

### Strategy 1: Unit Tests with Mocked Dependencies

**Goal**: Test component logic in complete isolation.

**Pattern**: Use `mocked_container` fixture or override providers.

```python
def test_isolated_component(mocked_container):
    """Test component without real DjangoSettings."""
    config = mocked_container.celery_config()
    
    # Verify mock values are used
    assert config["broker_url"] == "redis://localhost:6379/0"
    assert config["timezone"] == "UTC"
```

**When to use**: Testing business logic that shouldn't depend on environment.

### Strategy 2: Provider Override Pattern

**Goal**: Test with different configurations dynamically.

**Pattern**: Use context managers to override specific providers.

```python
def test_with_custom_config(container):
    """Test component with custom configuration."""
    custom_config = {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "timezone": "America/Sao_Paulo",
        # ... other settings
    }
    
    with container.celery_config.override(providers.Object(custom_config)):
        config = container.celery_config()
        assert config["broker_url"] == "memory://"
```

**When to use**: Testing how component behaves with different configurations.

### Strategy 3: Configuration Override Pattern

**Goal**: Test with mocked Pydantic settings.

**Pattern**: Override the Configuration provider with mocked DjangoSettings.

```python
def test_with_mocked_settings(container, mock_settings):
    """Test with completely mocked DjangoSettings."""
    mock_settings.celery_timezone = "Asia/Tokyo"
    
    with container.config.override(
        providers.Configuration(pydantic_settings=[mock_settings])
    ):
        config = container.celery_config()
        assert config["timezone"] == "Asia/Tokyo"
```

**When to use**: Testing integration with settings layer.

### Strategy 4: Nested Overrides

**Goal**: Test multiple override scenarios in same test.

**Pattern**: Nest context managers for layered overrides.

```python
def test_nested_overrides(container, mock_settings, alternative_mock_settings):
    """Test that overrides can be nested and restored."""
    with container.config.override(
        providers.Configuration(pydantic_settings=[mock_settings])
    ):
        config1 = container.celery_config()
        assert config1["timezone"] == "UTC"
        
        with container.config.override(
            providers.Configuration(pydantic_settings=[alternative_mock_settings])
        ):
            config2 = container.celery_config()
            assert config2["timezone"] == "America/Sao_Paulo"
        
        # After exiting inner context, first override is restored
        config3 = container.celery_config()
        assert config3["timezone"] == "UTC"
```

**When to use**: Testing override behavior and ensuring proper cleanup.

### Strategy 5: Parametrized Tests

**Goal**: Test same logic with multiple input sets.

**Pattern**: Use `pytest.mark.parametrize`.

```python
@pytest.mark.parametrize(
    ("broker_url", "expected_type"),
    [
        ("amqp://localhost", "rabbitmq"),
        ("redis://localhost", "redis"),
        ("kafka://localhost", "kafka"),
    ],
)
def test_broker_detection(container, mock_settings, broker_url, expected_type):
    """Test broker type detection from URL."""
    mock_settings.effective_broker_url = broker_url
    
    with container.config.override(
        providers.Configuration(pydantic_settings=[mock_settings])
    ):
        config = container.celery_config()
        assert config["broker_url"] == broker_url
```

**When to use**: Testing behavior across multiple scenarios.

## Available Fixtures

### Core Fixtures (conftest.py)

#### `reset_celery_singleton` (autouse)

Automatically resets Celery singleton before and after each test.

```python
# Automatically applied to all tests
def test_something():
    app = get_celery_app("test")  # Always fresh singleton
```

#### `container`

Provides a fresh `KiwiContainer` instance.

```python
def test_with_container(container):
    assert isinstance(container, KiwiContainer)
    config = container.celery_config()
```

#### `mock_settings`

Mock `DjangoSettings` with standard test configuration.

```python
def test_with_mock_settings(mock_settings):
    assert mock_settings.effective_broker_url == "redis://localhost:6379/0"
    assert mock_settings.celery_timezone == "UTC"
    mock_settings.celery_task_time_limit = 7200  # Can modify
```

#### `mocked_container`

Container with pre-applied mock settings override.

```python
def test_with_mocked_container(mocked_container):
    # Container already has mock_settings applied
    config = mocked_container.celery_config()
    assert config["broker_url"] == "redis://localhost:6379/0"
```

#### `alternative_mock_settings`

Alternative mock settings for testing multiple configurations.

```python
def test_switching_configs(container, mock_settings, alternative_mock_settings):
    with container.config.override(
        providers.Configuration(pydantic_settings=[mock_settings])
    ):
        config1 = container.celery_config()
    
    with container.config.override(
        providers.Configuration(pydantic_settings=[alternative_mock_settings])
    ):
        config2 = container.celery_config()
    
    assert config1["broker_url"] != config2["broker_url"]
```

## Examples

### Example 1: Basic Unit Test

```python
def test_celery_config_structure(mocked_container):
    """Test that celery_config returns correct structure."""
    config = mocked_container.celery_config()
    
    required_keys = {
        "broker_url", "result_backend", "timezone",
        "task_serializer", "result_serializer"
    }
    assert all(key in config for key in required_keys)
```

### Example 2: Override Single Provider

```python
def test_custom_celery_config(container):
    """Test Celery app creation with custom config."""
    custom_config = {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "timezone": "UTC",
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "task_track_started": True,
        "task_time_limit": 3600,
        "task_soft_time_limit": 3300,
        "worker_prefetch_multiplier": 1,
        "worker_max_tasks_per_child": 1000,
    }
    
    with container.celery_config.override(providers.Object(custom_config)):
        from django_tools.kiwi.celery import create_celery_app
        
        # Temporarily patch container instantiation
        original_container = container
        
        app = create_celery_app("test_app")
        assert app.conf.broker_url == "memory://"
```

### Example 3: Test Configuration Changes

```python
def test_timezone_configuration(container, mock_settings):
    """Test that timezone changes are reflected."""
    timezones = ["UTC", "America/Sao_Paulo", "Europe/London", "Asia/Tokyo"]
    
    for tz in timezones:
        mock_settings.celery_timezone = tz
        
        with container.config.override(
            providers.Configuration(pydantic_settings=[mock_settings])
        ):
            config = container.celery_config()
            assert config["timezone"] == tz
```

### Example 4: Integration Test

```python
@pytest.mark.integration
def test_end_to_end_celery_setup(container):
    """Test complete Celery setup flow."""
    from django_tools.kiwi import create_celery_app
    
    # Get config from container
    config = container.celery_config()
    
    # Create Celery app
    app = create_celery_app("integration_test")
    
    # Verify configuration was applied
    assert app.conf.broker_url == config["broker_url"]
    assert app.conf.result_backend == config["result_backend"]
    
    # Define and test task
    @app.task
    def add(x: int, y: int) -> int:
        return x + y
    
    result = add(2, 3)
    assert result == 5
```

### Example 5: Testing Task Behavior

```python
def test_celery_task_configuration():
    """Test that tasks are properly configured."""
    from django_tools.kiwi import get_celery_app
    
    app = get_celery_app("task_test")
    
    @app.task(bind=True, max_retries=3)
    def retry_task(self, value: int) -> int:
        return value * 2
    
    # Test task metadata
    assert retry_task.max_retries == 3
    assert callable(retry_task)
    
    # Test task execution
    result = retry_task(21)
    assert result == 42
```

## Best Practices

### 1. Use Fixtures for Common Setup

```python
# Good: Reusable fixture
@pytest.fixture
def redis_settings(mock_settings):
    mock_settings.effective_broker_url = "redis://localhost:6379/0"
    return mock_settings

def test_with_redis(container, redis_settings):
    with container.config.override(
        providers.Configuration(pydantic_settings=[redis_settings])
    ):
        config = container.celery_config()
        assert "redis" in config["broker_url"]
```

### 2. Test Isolation

```python
# Good: Each test is independent
def test_scenario_a(mocked_container):
    config = mocked_container.celery_config()
    # Test scenario A

def test_scenario_b(mocked_container):
    config = mocked_container.celery_config()
    # Test scenario B - no interference from A
```

### 3. Meaningful Test Names

```python
# Good: Descriptive names
def test_celery_config_uses_redis_broker_from_settings():
    ...

def test_container_override_restores_original_config_after_context():
    ...
```

### 4. Use Context Managers for Overrides

```python
# Good: Automatic cleanup
def test_with_override(container, mock_settings):
    with container.config.override(
        providers.Configuration(pydantic_settings=[mock_settings])
    ):
        # Test with override
        ...
    # Original config automatically restored
```

### 5. Test Both Success and Failure Cases

```python
def test_valid_broker_url(container, mock_settings):
    mock_settings.effective_broker_url = "redis://localhost:6379/0"
    # Test success case
    ...

def test_invalid_broker_url_raises_error(container, mock_settings):
    mock_settings.effective_broker_url = "invalid://url"
    # Test failure case
    with pytest.raises(SomeException):
        ...
```

## Coverage Goals

- **Overall**: > 90%
- **Critical paths**: 100%
- **Kiwi module**: > 95%

Generate coverage report:

```bash
pytest --cov=django_tools --cov-report=html --cov-report=term-missing
```

## Continuous Integration

Tests should run automatically on:

- Every push to main branch
- Every pull request
- Release tags

Ensure tests pass before merging!

## Further Reading

- [Dependency Injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Use dependency injection patterns
3. Add fixtures to `conftest.py` if reusable
4. Document complex test patterns
5. Ensure > 90% coverage
