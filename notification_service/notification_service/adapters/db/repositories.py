from uuid import UUID

from notification_service.application.ports.repositories import (
    NotificationRepositoryPort
)
from notification_service.domain.entities import Notification
from notification_service.domain.enums import NotificationStatus
from notification_service.adapters.db.models import NotificationModel
from notification_service.application.ports.exceptions.repository import (
    ObjectNotFoundInRepository
)


class DjangoNotificationRepository(NotificationRepositoryPort):
    """
    Django ORM-based notification repository.
    Provides CRUD operations for notifications using Django models.
    """
    def exists(self, uuid: UUID) -> bool:
        """
        Check if a notification with the specified UUID exists.

        Parameters
        ----------
        uuid : UUID
            UUID of the notification to check

        Returns
        ----------
        bool
            True if notification exists, False otherwise
        """
        return NotificationModel.objects.filter(uuid=uuid).exists()

    def get_by_uuid(self, uuid: UUID) -> Notification:
        """
        Get notification by it's UUID.

        Parameters
        ----------
        uuid : UUID
            UUID of the notification

        Returns
        ----------
        Notification
            Notification object

        Raises
        ----------
        ObjectNotFoundInRepository
            If notification is not found
        """
        obj = NotificationModel.objects.filter(uuid=uuid).first()
        if not obj:
            raise ObjectNotFoundInRepository()
        return self._model_to_entity(obj)

    def create(self, notification: Notification) -> Notification:
        """
        Create a new notification.

        Parameters
        ----------
        notification : Notification
            Notification object to create

        Returns
        ----------
        Notification
            Created notification object
        """
        notification = NotificationModel.objects.create(
            uuid=notification.uuid,
            user_uuid=notification.user_uuid,
            title=notification.title,
            text=notification.text,
            type=notification.type,
        )
        return self._model_to_entity(notification)

    def update(self, notification: Notification) -> Notification:
        """
        Update an existing notification.

        Parameters
        ----------
        notification : Notification
            Notification object with updated data

        Returns
        ----------
        Notification
            Updated notification object

        Raises
        ----------
        ObjectNotFoundInRepository
            If notification is not found for update
        """
        updated = (
            NotificationModel.objects
            .filter(uuid=notification.uuid)
            .update(
                user_uuid=notification.user_uuid,
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
        """
        Get pending notification for update, locking a row while transaction is alive.

        Returns
        ----------
        Notification | None
            Notification object or None, if there are no pending notifications 
        """
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
        """
        Convert Django model to notification entity.

        Parameters
        ----------
        model : NotificationModel
            Django notification model

        Returns
        ----------
        Notification
            Notification entity object
        """
        return Notification(
            uuid=model.uuid,
            user_uuid=model.user_uuid,
            title=model.title,
            text=model.text,
            type=model.type,
            status=model.status
        )