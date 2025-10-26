"""Example usage of Kiwi module with Django Tools."""

from django_tools.kiwi import get_celery_app

# Example 1: Basic usage - Get Celery app singleton
# =====================================================
# The Celery app is automatically configured from your .env file
# or environment variables via DjangoSettings
celery_app = get_celery_app("my_app")


# Example 2: Define tasks using the singleton
# =====================================================
@celery_app.task
def send_email(to: str, subject: str, body: str) -> dict[str, str]:
    """Example task to send email."""
    # Your email logic here
    return {"status": "sent", "to": to, "subject": subject}


@celery_app.task
def process_data(data_id: int) -> dict[str, int]:
    """Example task to process data."""
    # Your processing logic here
    return {"status": "processed", "data_id": data_id}


# Example 3: Using with Django settings.py
# =====================================================
# In your Django settings.py, you can use DjangoSettings directly:
#
# from django_tools.settings import DjangoSettings
# from django_tools.kiwi import get_celery_app
#
# settings = DjangoSettings(env_file=".env")
#
# # Django settings
# SECRET_KEY = settings.secret_key
# DEBUG = settings.debug
# DATABASES = settings.databases
# ALLOWED_HOSTS = settings.allowed_hosts
#
# # Celery configuration (already applied to the singleton)
# celery_app = get_celery_app(__name__)


# Example 4: Using the container directly for advanced scenarios
# =====================================================
from django_tools.kiwi import KiwiContainer

container = KiwiContainer()
celery_config = container.celery_config()
print(f"Broker URL: {celery_config['broker_url']}")
print(f"Result Backend: {celery_config['result_backend']}")


# Example 5: Calling tasks
# =====================================================
if __name__ == "__main__":
    # Call task asynchronously
    result = send_email.delay("user@example.com", "Hello", "Test email")
    print(f"Task ID: {result.id}")

    # Call task synchronously (for testing)
    result = process_data.apply_async(args=[123], countdown=10)
    print(f"Task will be executed in 10 seconds: {result.id}")
