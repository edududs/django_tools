from celery import Celery

app = Celery("kiwi_tasks")

# Configura a app Celery a partir das settings do Django.
# Isso instrui o Celery a buscar TODAS as variáveis globais que
# começam com CELERY_ no módulo django.conf.settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodescoberta de tarefas.
# O Celery fará o autodiscover em todas as apps listadas em INSTALLED_APPS
# (incluindo as apps da sua lib, se houver).
app.autodiscover_tasks()
