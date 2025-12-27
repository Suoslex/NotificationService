from notification_service.application.ports.repositories import (
    NotificationRepositoryPort
)
from notification_service.domain.entities import Notification
from notification_service.domain.enums import NotificationStatus
from notification_service.adapters.db.models import NotificationModel
from notification_service.application.ports.exceptions import (
    ObjectNotFoundInRepository
)


class DjangoNotificationRepository(NotificationRepositoryPort):
    def exists(self, uuid: str) -> bool:
        return NotificationModel.objects.filter(uuid=uuid).exists()

    def get_by_uuid(self, uuid: str) -> Notification:
        obj = NotificationModel.objects.filter(uuid=uuid).first()
        if not obj:
            raise ObjectNotFoundInRepository()
        return self._model_to_entity(obj)

    def create(self, notification: Notification) -> Notification:
        notification = NotificationModel.objects.create(
            uuid=notification.uuid,
            user_id=notification.user_id,
            title=notification.title,
            text=notification.text,
            type=notification.type,
        )
        return self._model_to_entity(notification)

    def update(self, notification: Notification) -> Notification:
        updated = (
            NotificationModel.objects
            .filter(uuid=notification.uuid)
            .update(
                user_id=notification.user_id,
                title=notification.title,
                text=notification.text,
                type=notification.type,
                status=notification.status,
            )
        )
        if not updated:
            raise ObjectNotFoundInRepository()
        return notification

    def get_pending_for_update(self) -> Notification | None:
        obj = (
            NotificationModel.objects
            .select_for_update(skip_locked=True)
            .filter(status=NotificationStatus.PENDING)
            .order_by("created_at")
            .first()
        )
        return self._model_to_entity(obj) if obj else None

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