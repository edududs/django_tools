# django_tools 🛠️

A comprehensive collection of utilities that standardize Django project configurations and provide essential tools for modern web development. This library offers reusable components that simplify project bootstrapping and serve as a foundation for scalable applications.

## ✨ Overview

This library provides modular tools organized by functionality:

- **Settings Management**: Advanced configuration handling with environment support, automatic detection, and seamless Django integration
- **Queue Management**: Celery integration with automatic configuration and dependency injection
- **Utilities**: Helper functions for common Django development tasks
- **Constants**: Reusable mappings and configurations for Django projects

## 🚀 Key Features

### Settings Management

- **Multi-environment support**: Load different configuration files for various environments
- **Automatic detection**: Intelligently detects database types, brokers, and other services from URLs
- **Flexible configuration**: Support for both URL-based and field-based configuration
- **Environment priority**: Environment variables > configuration files > sensible defaults
- **Django integration**: Seamless integration with Django's settings system

### Queue Management

- **Celery integration**: Pre-configured Celery applications with automatic settings
- **Dependency injection**: Modern dependency injection patterns for better testability
- **Zero configuration**: Works out-of-the-box with your environment files
- **Multiple brokers**: Support for RabbitMQ, Redis, and other message brokers

### Utilities

- **Environment setup**: Tools for preparing Django environments in standalone scripts
- **Configuration helpers**: Utilities for common configuration tasks
- **Development tools**: Helper functions for development and testing

## 📖 Usage Examples

### Quick Start

```python
from django_tools.settings import Settings

# Load configuration from environment
settings = Settings()

# Access Django-compatible configurations
django_config = settings.to_dict()
print(settings.databases)  # Database configuration
print(settings.celery_config)  # Celery configuration
```

### Environment-Specific Configuration

```python
# Load specific configuration file
settings = Settings(env_file=".env.production")

# Load from directory
settings = Settings(env_dir="/path/to/config")

# Mix environment variables with configuration files
import os
os.environ["SECRET_KEY"] = "override-from-env"
settings = Settings(env_file=".env.staging")
```

### Queue Management Example

```python
from django_tools.kiwi import get_celery_app

# Get pre-configured Celery app
celery_app = get_celery_app("my_app")

# Define and use tasks
@celery_app.task
def process_data(data):
    return {"status": "processed", "data": data}

result = process_data.delay({"key": "value"})
```

## 🔧 Configuration

### Basic Configuration File

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Message Broker
BROKER_URL=amqp://user:password@localhost:5672/

# Cache/Queue
REDIS_URL=redis://:password@localhost:6379/0

# Application Settings
API_NAME=my_api
LANGUAGE_CODE=en-us
TIME_ZONE=UTC
```

### Production Configuration

```bash
# Production Database
DATABASE_URL=postgresql://prod_user:secure_password@db.example.com:5432/prod_db

# Security
SECRET_KEY=very-long-and-secure-production-secret
DEBUG=False
ALLOWED_HOSTS=api.example.com,www.example.com

# Production Broker
BROKER_URL=amqp://prod_user:secure_pass@rabbitmq.example.com:5672/prod_vhost

# Production Cache
REDIS_URL=redis://:secure_password@redis.example.com:6379/0

# Application
API_NAME=production_api
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo
```

## 🔄 Auto-Detection Features

The library automatically detects and configures:

- **Database types**: PostgreSQL, MySQL, SQLite from connection URLs
- **Message brokers**: RabbitMQ, Redis, Kafka from URLs or hostnames
- **Service configurations**: Automatic parameter extraction from service URLs
- **Environment-specific settings**: Different configurations for development, staging, production

## 🚧 Project Status

- **Current version**: `0.2.x` - Core functionality stable
- **API stability**: Breaking changes may occur in minor versions
- **Documentation**: Continuously expanding with new features and examples
- **Production ready**: Core components are production-ready with comprehensive configuration support

## 📚 Documentation

- **Feature-based organization**: Documentation organized by functionality rather than implementation details
- **Configuration examples**: Detailed examples for different environments and use cases
- **Advanced usage**: Auto-detection, computed properties, and multi-environment support
- **Contributing**: Feedback and suggestions help prioritize upcoming features

## 🔄 Migration Guide

When upgrading between versions:

1. **Configuration changes**: Check for new configuration options and deprecated settings
2. **API updates**: Review breaking changes in the changelog
3. **New features**: Explore new functionality and configuration options
4. **Best practices**: Follow updated recommendations for configuration management

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

⭐ If this project helped you, consider giving it a star!
