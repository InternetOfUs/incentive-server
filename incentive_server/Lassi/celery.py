import os

from celery import Celery
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lassi.settings")

app = Celery("Lassi", broker='redis://redis:6379/0')
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(settings.INSTALLED_APPS)
# app = Celery("Lassi")
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()