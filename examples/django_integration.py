"""Example Django settings.py integration with django_tools."""

from pathlib import Path

from django_tools.kiwi import get_celery_app
from django_tools.settings import DjangoSettingsBaseModel

# Initialize settings from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
settings = DjangoSettingsBaseModel(env_file=str(BASE_DIR / ".env"))

# Core Django Settings
SECRET_KEY = settings.secret_key
DEBUG = settings.debug
ALLOWED_HOSTS = settings.allowed_hosts

# Application definition
INSTALLED_APPS = [
    *settings.default_installed_apps,
    # Your apps here
    "myapp",
]

MIDDLEWARE = settings.default_middleware

ROOT_URLCONF = "myproject.urls"
WSGI_APPLICATION = "myproject.wsgi.application"

# Database
DATABASES = settings.databases

# Password validation
AUTH_PASSWORD_VALIDATORS = settings.default_auth_password_validators

# Internationalization
LANGUAGE_CODE = settings.language_code
TIME_ZONE = settings.time_zone
USE_I18N = settings.use_i18n
USE_TZ = settings.use_tz

# Templates
TEMPLATES = settings.templates

# Static files
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = settings.default_auto_field

# Logging
LOGGING = settings.default_logging

# Celery Configuration (automatically configured via singleton)
celery_app = get_celery_app(__name__)

# Additional Celery settings can be accessed via settings.celery_config
# The celery_app singleton is already configured with these values
