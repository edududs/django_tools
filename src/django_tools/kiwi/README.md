# Kiwi - Queue Management Module

Queue management module with automatic integration between Django, Pydantic, and Celery using Dependency Injection.

## Features

- **Celery Singleton**: Single instance automatically configured from `DjangoSettings`
- **Zero Configuration**: Works immediately with your `.env` file
- **Dependency Injection**: Integrated container with `dependency-injector` and Pydantic
- **Type Safety**: Fully typed with Python 3.12+
- **Pythonic**: Clean, idiomatic code following best practices

## Quick Start

### Basic Usage

```python
from django_tools.kiwi import get_celery_app

# Get Celery singleton (auto-configured from .env)
celery_app = get_celery_app("my_app")

# Define tasks
@celery_app.task
def process_order(order_id: int) -> dict[str, int]:
    # Your logic here
    return {"status": "processed", "order_id": order_id}

# Execute tasks
result = process_order.delay(123)
```

### Django Integration

```python
# settings.py
from django_tools.settings import DjangoSettings
from django_tools.kiwi import get_celery_app

settings = DjangoSettings()

# Django settings
SECRET_KEY = settings.secret_key
DATABASES = settings.databases

# Celery (singleton, auto-configured)
celery_app = get_celery_app(__name__)
```

### Advanced Usage - Container

```python
from django_tools.kiwi import KiwiContainer

# Access container directly
container = KiwiContainer()
celery_config = container.celery_config()

# Inspect configuration
print(f"Broker: {celery_config['broker_url']}")
print(f"Backend: {celery_config['result_backend']}")
print(f"Timezone: {celery_config['timezone']}")
```

## Architecture

### Components

1. **`KiwiContainer`**: Dependency Injection Container
   - Integrates with `DjangoSettings` via Pydantic
   - Provides providers for Celery configuration
   - Allows extension with new providers

2. **`create_celery_app()`**: Factory for creating Celery instances
   - Creates new configured instance
   - Applies settings from `DjangoSettings`
   - Auto-discovers tasks

3. **`get_celery_app()`**: Celery Singleton
   - Always returns the same instance
   - Lazy loading (creates on first call)
   - Thread-safe

### Configuration Flow

```text
.env file
    ↓
DjangoSettings (Pydantic)
    ↓
KiwiContainer (Dependency Injector)
    ↓
Celery App (Singleton)
    ↓
Your Tasks
```

## Configuration (.env)

```bash
# Broker Configuration
BROKER_URL=amqp://user:pass@localhost:5672/

# Celery Settings
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TIMEZONE=America/Sao_Paulo
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3300
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000
```

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/test_kiwi.py -v

# With coverage
pytest tests/test_kiwi.py --cov=django_tools.kiwi --cov-report=html
```

## Design Principles

- **KISS**: Simplicity first
- **YAGNI**: Implement only what's necessary
- **Single Responsibility**: Each module has a clear responsibility
- **Dependency Injection**: Facilitates testing and extensibility
- **Type Safety**: Complete typing for better IDE support

## Extensibility

### Add New Providers

```python
from django_tools.kiwi import KiwiContainer
from dependency_injector import providers

class CustomContainer(KiwiContainer):
    # Add custom providers
    custom_service = providers.Singleton(
        MyCustomService,
        config=KiwiContainer.config,
    )
```

### Create Multiple Instances

```python
from django_tools.kiwi import create_celery_app

# Create separate instances for different purposes
app_email = create_celery_app("email_worker")
app_data = create_celery_app("data_worker")
```

## API Reference

### `get_celery_app(app_name: str = "django_tools") -> Celery`

Get or create singleton Celery application instance.

**Parameters:**
- `app_name`: Name for the Celery application (only used on first call)

**Returns:**
- Singleton Celery application instance

**Example:**
```python
app = get_celery_app("my_app")
```

### `create_celery_app(app_name: str = "django_tools") -> Celery`

Create and configure a new Celery application from DjangoSettings.

**Parameters:**
- `app_name`: Name for the Celery application

**Returns:**
- Configured Celery application instance

**Example:**
```python
app = create_celery_app("my_app")
```

### `class KiwiContainer`

Dependency Injection container for Kiwi queue management dependencies.

**Providers:**
- `config`: Configuration provider from DjangoSettings
- `celery_config`: Dict provider with complete Celery configuration

**Example:**
```python
container = KiwiContainer()
config = container.celery_config()
```

## Examples

See the `examples/` directory for more usage examples:

- `examples/kiwi_usage.py` - Basic usage examples
- `examples/celery_app.py` - Standard Django project setup
- `examples/django_integration.py` - Full Django integration
