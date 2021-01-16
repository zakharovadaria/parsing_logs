import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parsing_logs.settings")

celery_app = Celery(
    "parsing_logs",
    broker=settings.CELERY_BROKER_URL,
)

celery_app.autodiscover_tasks()
