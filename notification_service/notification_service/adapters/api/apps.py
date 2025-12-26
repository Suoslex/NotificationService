from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'notification_service.adapters.api'

    def ready(self):
        self._import_models()

    def _import_models(self):
        from notification_service.adapters.db import models
