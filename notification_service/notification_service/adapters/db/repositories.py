from notification_service.application.ports.repositories import (
    NotificationRepositoryPort
)
from notification_service.domain.entities import Notification
from notification_service.adapters.db.models import NotificationModel


class DjangoNotificationRepository(NotificationRepositoryPort):
    def exists(self, uuid: str) -> bool:
        return NotificationModel.objects.filter(uuid=uuid).exists()

    def get_by_uuid(self, uuid: str) -> Notification | None:
        obj = NotificationModel.objects.filter(uuid=uuid).first()
        return self._model_to_entity(obj) if obj else None

    def create(self, notification: Notification) -> Notification:
        notification = NotificationModel.objects.create(
            uuid=notification.uuid,
            user_id=notification.user_id,
            title=notification.title,
            text=notification.text,
            type=notification.type,
        )
        return self._model_to_entity(notification)

    @staticmethod
    def _model_to_entity(model: NotificationModel) -> Notification:
        return Notification(
            uuid=model.uuid,
            user_id=model.user_id,
            title=model.title,
            text=model.text,
            type=model.type,
            status=model.status
        )