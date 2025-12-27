import os

from celery import Celery

from notification_service.config.settings import base


celery_app = Celery("notification_service")
celery_app.config_from_object(
    os.environ.get("DJANGO_SETTINGS_MODULE"),
    namespace="CELERY"
)
celery_app.autodiscover_tasks(["notification_service.adapters.workers.celery"])


