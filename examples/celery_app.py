"""Standard Celery app configuration for Django projects.

Place this file in your Django project root (e.g., myproject/celery.py)
alongside your settings.py file.

Usage in __init__.py:
    from .celery import celery_app

    __all__ = ["celery_app"]

Run worker:
    celery -A myproject worker -l info

Run beat (scheduler):
    celery -A myproject beat -l info
"""

import os

from django_tools.kiwi import get_celery_app

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

# Get pre-configured Celery singleton
celery_app = get_celery_app("myproject")

# Optional: Add custom configuration
celery_app.conf.update(
    task_routes={
        "myapp.tasks.send_email": {"queue": "emails"},
        "myapp.tasks.process_image": {"queue": "images"},
    },
    task_annotations={
        "myapp.tasks.slow_task": {"rate_limit": "10/m"},
    },
)

# Auto-discover tasks from installed apps
# This is already done by get_celery_app, but you can customize
# celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
