# django_tools 🛠️

A comprehensive collection of utilities that standardize Django project configurations for APIs. This library provides reusable components that simplify project bootstrapping and serve as a foundation for future expansions.

## ✨ Overview

- `settings.DjangoSettings`: Advanced Pydantic-based class that centralizes Django configurations with support for multiple environments, automatic broker detection, and computed properties for seamless Django integration.
- `settings.consts`: Constants and mappings used to export configurations in Django-compatible dictionary format.
- `utils.setup`: Utilities for preparing Django environment in standalone scripts.
- `kiwi.celery`: Pre-configured Celery application that consumes Django `CELERY_` variables.

## 🚀 Key Features

### DjangoSettings Class

- **Multi-environment support**: Load different `.env` files (e.g., `.env.production`, `.env.staging`)
- **Automatic broker detection**: Intelligently detects broker types (RabbitMQ, Redis, Kafka) from URLs
- **Computed properties**: Provides Django-compatible configuration dictionaries
- **Comprehensive coverage**: Database, security, Celery, Redis, templates, and logging settings
- **Environment priority**: Environment variables > `.env` file > defaults

## 📖 Usage Examples

### Basic Usage

```python
from django_tools.settings import DjangoSettings

# Load from environment variables or default .env file
settings = DjangoSettings()

# Access Django-compatible configurations
django_config = settings.to_dict()
print(settings.databases)  # {'default': {'ENGINE': '...', 'NAME': '...'}}
print(settings.celery_config)  # Complete Celery configuration
print(settings.broker_type)  # Auto-detected: 'rabbitmq', 'redis', etc.
```

### Environment-Specific Configuration

```python
# Load specific .env file
settings = DjangoSettings(env_file=".env.production")

# Load from directory (looks for .env in that directory)
settings = DjangoSettings(env_dir="/path/to/config")

# Mix environment variables with .env file
import os
os.environ["SECRET_KEY"] = "override-from-env"
settings = DjangoSettings(env_file=".env.staging")
# SECRET_KEY will use environment variable value
```

### Advanced Configuration Access

```python
settings = DjangoSettings()

# Database configuration
db_config = settings.databases
print(db_config["default"]["ENGINE"])  # Database engine

# Broker configuration with auto-detection
broker_config = settings.broker_config
print(broker_config["type"])  # 'rabbitmq', 'redis', 'kafka'
print(broker_config["url"])   # Complete broker URL

# Redis configuration
redis_config = settings.redis_config
print(redis_config["host"])   # Redis host
print(redis_config["db"])    # Redis database number

# Template configuration
templates = settings.templates
print(templates[0]["BACKEND"])  # Template backend

# Default Django configurations
installed_apps = settings.default_installed_apps
middleware = settings.default_middleware
logging_config = settings.default_logging
```

## 🔧 Environment Configuration

### Basic .env File

```bash
# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=myapp_db
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Broker Configuration (Option 1: Complete URL)
BROKER_URL=amqp://admin:admin@localhost:5672/

# Broker Configuration (Option 2: Separate Variables)
BROKER_HOST=localhost
BROKER_PORT=5672
BROKER_USER=admin
BROKER_PASSWORD=admin
BROKER_VHOST=/

# Celery Configuration
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TIMEZONE=UTC
CELERY_TASK_TIME_LIMIT=3600

# Redis Configuration
REDIS_URL=redis://:password@localhost:6379/0
# OR separate variables:
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=password

# Application Settings
API_NAME=my_api
LANGUAGE_CODE=en-us
TIME_ZONE=UTC
```

### Production .env File Example

```bash
# Production Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=production_db
DB_USER=prod_user
DB_PASSWORD=secure_production_password
DB_HOST=db.example.com
DB_PORT=5432

# Security
SECRET_KEY=very-long-and-secure-production-secret-key
DEBUG=False
ALLOWED_HOSTS=api.example.com,www.example.com

# Production Broker
BROKER_URL=amqp://prod_user:secure_pass@rabbitmq.example.com:5672/prod_vhost

# Production Redis
REDIS_URL=redis://:secure_redis_password@redis.example.com:6379/0

# Celery Production Settings
CELERY_RESULT_BACKEND=redis://:secure_redis_password@redis.example.com:6379/2
CELERY_TIMEZONE=America/Sao_Paulo
CELERY_TASK_TIME_LIMIT=7200
CELERY_WORKER_MAX_TASKS_PER_CHILD=500

# Application
API_NAME=production_api
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo
```

### Broker Type Auto-Detection

The system automatically detects broker types based on URLs or hostnames:

```bash
# RabbitMQ (detected from amqp:// or hostname containing 'rabbit')
BROKER_URL=amqp://user:pass@rabbitmq.example.com:5672/vhost
# OR
BROKER_HOST=rabbitmq.example.com

# Redis (detected from redis:// or hostname containing 'redis')
BROKER_URL=redis://:pass@redis.example.com:6379/0
# OR
BROKER_HOST=redis.example.com

# Kafka (detected from hostname containing 'kafka')
BROKER_HOST=kafka.example.com
BROKER_PORT=9092
```

## 🚧 Project Status

- **Current version**: `0.2.x` - Core functionality stable
- **API stability**: Breaking changes may occur in minor versions
- **Documentation**: Continuously expanding with new features and examples
- **Production ready**: DjangoSettings class is production-ready with comprehensive configuration support

## 📚 Documentation

- **Complete examples**: All major use cases covered in this README
- **Environment configuration**: Detailed `.env` file examples for different scenarios
- **Advanced usage**: Broker auto-detection, computed properties, and multi-environment support
- **Contributing**: Feedback and suggestions help prioritize upcoming features

## 🔄 Migration Guide

If you're upgrading from previous versions:

1. **DjangoSettings**: Now uses English docstrings and improved computed properties
2. **Broker detection**: Automatic broker type detection from URLs or hostnames
3. **Environment files**: Enhanced support for multiple `.env` files
4. **Configuration access**: New computed properties for easier Django integration

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

⭐ If this project helped you, consider giving it a star!
