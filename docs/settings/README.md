# Django Tools Settings

Configuration system based on Pydantic Settings for Django applications, with support for multiple infrastructures (Database, Celery, Redis, RabbitMQ).

## Features

- **Automatic validation** via Pydantic v2
- **Bidirectional conversion** URL ↔ individual fields (Redis, RabbitMQ)
- **Multiple aliases** for environment variables (e.g., `DATABASE_URL` or `DB_URL`)
- **Type-safe** with full type annotations
- **.env files** loaded via `_env_file`
- **94% test coverage** currently

## Structure

```
settings/
├── base/
│   ├── __init__.py          # Main Settings class
│   ├── settings_django.py   # Django settings
│   └── infra/
│       ├── settings_database.py  # Database (PostgreSQL, MySQL, SQLite)
│       ├── settings_celery.py    # Celery (broker, workers, beat)
│       ├── settings_redis.py     # Redis (URL or separate fields)
│       └── settings_rabbit.py    # RabbitMQ (URL or separate fields)
└── tests/
    ├── conftest.py          # Test fixtures
    └── test_settings.py     # 27 organized tests
```

## How to Use

### Basic Usage

```python
from django_tools.settings import Settings

# Load from default .env
settings = Settings()

# Load from specific file
settings = Settings(env_file="production.env")

# Access configurations
print(settings.dj.secret_key)
print(settings.db.url)
print(settings.redis.host)
```

### Individual Settings Usage

```python
from django_tools.settings.base.infra import RedisSettings, RabbitMQSettings

# Redis via URL
redis = RedisSettings(_env_file=".env")
print(redis.host, redis.port, redis.db)  # Extracted from URL

# RabbitMQ via fields
rabbit = RabbitMQSettings(
    RABBIT_HOST="localhost",
    RABBIT_PORT=5672,
    RABBIT_USERNAME="admin",
    RABBIT_PASSWORD="admin"
)
print(rabbit.url)  # URL is automatically built
```

## How It Works

### Loading Flow

1. **Initialization**: `Settings(env_file=".env")`
2. **Pydantic Settings** loads variables from the `.env` file
3. **Model Validators** process values (conversions, aliases)
4. **Field Validators** validate specific fields (e.g., `allowed_hosts`)
5. **Ready instance** with validated, typed values

### Bidirectional Conversion (Redis/RabbitMQ)

#### URL → Fields

```python
# .env
REDIS_URL="redis://:pass@localhost:6379/2"

# Result
redis.url = "redis://:pass@localhost:6379/2"
redis.host = "localhost"
redis.port = 6379
redis.db = 2
redis.password = "pass"
```

#### Fields → URL

```python
# .env
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=2
REDIS_PASSWORD="pass"

# Result
redis.url = "redis://:pass@localhost:6379/2"  # Automatically built
redis.host = "localhost"
redis.port = 6379
```

### Validation Aliases

Multiple names for the same variable:

```python
# Any works:
DATABASE_URL="postgresql://..."
DB_URL="postgresql://..."

DATABASE_NAME="mydb"
DB_NAME="mydb"

SECRET_KEY="secret"
DJANGO_SECRET_KEY="secret"
```

### Smart Parsing

**ALLOWED_HOSTS** accepts multiple formats:

```python
# JSON array
ALLOWED_HOSTS=["localhost","127.0.0.1"]

# CSV
ALLOWED_HOSTS="localhost,127.0.0.1"

# Python list
allowed_hosts=["localhost", "127.0.0.1"]
```

## Environment Variables

### Django

```bash
SECRET_KEY="your-secret-key"
DEBUG=false
ALLOWED_HOSTS=["localhost","127.0.0.1"]
TIME_ZONE="America/Sao_Paulo"
LANGUAGE_CODE="pt-br"
API_NAME="my-api"
```

### Database

```bash
# Option 1: full URL
DATABASE_URL="postgresql://user:pass@localhost:5432/db"

# Option 2: individual fields
DB_ENGINE="django.db.backends.postgresql"
DB_NAME="mydb"
DB_USER="user"
DB_PASSWORD="pass"
DB_HOST="localhost"
DB_PORT=5432
DB_CONN_MAX_AGE=300
DB_CONN_HEALTH_CHECKS=true
```

### Celery

```bash
CELERY_BROKER_URL="amqp://guest:guest@localhost:5672/"
CELERY_RESULT_BACKEND="redis://localhost:6379/1"
CELERY_TIMEZONE="America/Sao_Paulo"
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_POOL="prefork"
CELERY_TASK_SERIALIZER="json"
CELERY_TASK_COMPRESSION="gzip"
```

### Redis

```bash
# Option 1: URL
REDIS_URL="redis://:password@localhost:6379/0"

# Option 2: fields
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD="password"
```

### RabbitMQ

```bash
# Option 1: URL
RABBIT_URL="amqp://user:pass@localhost:5672/vhost"

# Option 2: fields
RABBIT_HOST="localhost"
RABBIT_PORT=5672
RABBIT_USERNAME="guest"
RABBIT_PASSWORD="guest"
RABBIT_VHOST="/"
```

## Tests

### Coverage: 94%

**27 tests** organized into 6 classes:

#### TestDjangoSettings (6 tests)

- .env loading
- ALLOWED_HOSTS parsing (JSON, list, empty)
- Default values
- Validation aliases

#### TestDatabaseSettings (4 tests)

- Loading via URL
- Loading via fields
- Aliases (DATABASE_*vs DB_*)
- Default values

#### TestCelerySettings (3 tests)

- Loading from .env
- JSON fields (queues, routes, schedule)
- Default values

#### TestRedisSettings (5 tests)

- Conversion URL → fields
- Conversion fields → URL
- Loading URL only
- Loading fields only
- Default values

#### TestRabbitMQSettings (5 tests)

- Conversion URL → fields
- Conversion fields → URL
- Loading URL only
- Loading fields only
- Default values

#### TestSettingsContainer (4 tests)

- Full load
- Serialization (model_dump)
- String representation
- Access to components

### Run Tests

```bash
# All tests
pytest src/django_tools/settings/tests/

# With coverage
pytest src/django_tools/settings/tests/ --cov=src/django_tools/settings --cov-report=term-missing

# Specific test
pytest src/django_tools/settings/tests/test_settings.py::TestRedisSettings::test_url_to_fields_conversion -v
```

## Django Integration

```python
# settings.py
from django_tools.settings import Settings

settings = Settings()

# Django settings
SECRET_KEY = settings.dj.secret_key
DEBUG = settings.dj.debug
ALLOWED_HOSTS = settings.dj.allowed_hosts
TIME_ZONE = settings.dj.time_zone

# Database
DATABASES = {
    "default": {
        "ENGINE": settings.db.engine,
        "NAME": settings.db.name,
        "USER": settings.db.user,
        "PASSWORD": settings.db.password,
        "HOST": settings.db.host,
        "PORT": settings.db.port,
        "CONN_MAX_AGE": settings.db.conn_max_age,
    }
}

# Celery
CELERY_BROKER_URL = settings.celery.broker_url
CELERY_RESULT_BACKEND = settings.celery.result_backend
```

## Default Values

| Setting              | Default                                   |
|----------------------|-------------------------------------------|
| Django SECRET_KEY    | `"django-insecure-change-me-in-production"` |
| Django DEBUG         | `True`                                    |
| Django ALLOWED_HOSTS | `["*"]`                                   |
| Database ENGINE      | `"django.db.backends.sqlite3"`            |
| Database NAME        | `"db.sqlite3"`                            |
| Celery TIMEZONE      | `"UTC"`                                   |
| Redis HOST           | `"localhost"`                             |
| Redis PORT           | `6379`                                    |
| RabbitMQ HOST        | `"localhost"`                             |
| RabbitMQ USERNAME    | `"guest"`                                 |

## Best Practices

1. **Use .env files** for different environments (`.env.local`, `.env.production`)
2. **Never commit** .env files with real credentials
3. **Prefer URLs** for infrastructure configuration (more portable)
4. **Validate** your configuration on application startup
5. **Use type hints** to enjoy Pydantic's validation

## Troubleshooting

### .env file doesn't load

```python
# ❌ Wrong
settings = Settings(env_file=".env")

# ✅ Correct
settings = Settings(env_file=".env")  # This works!
```

### JSON fields in .env

```bash
# ❌ Wrong (string with quotes)
CELERY_TASK_QUEUES='[{"name":"high"}]'

# ✅ Correct (valid JSON)
CELERY_TASK_QUEUES=[{"name":"high"}]
```

### Conversion doesn't work

```bash
# For automatic conversion to work:
# Option 1: Provide ONLY the URL
REDIS_URL="redis://localhost:6379/0"

# Option 2: Provide ONLY the fields
REDIS_HOST="localhost"
REDIS_PORT=6379
```

## Architecture

```
Settings (container)
├── dj: DjangoSettingsBaseModel
│   ├── Loads Django variables
│   └── Validates ALLOWED_HOSTS
├── db: DatabaseSettings
│   └── Supports multiple aliases
├── celery: CelerySettings
│   └── Parses JSON fields
├── redis: RedisSettings
│   └── URL ↔ fields conversion
└── rabbit: RabbitMQSettings
    └── URL ↔ fields conversion
```

Each component is independent and can be used standalone.
