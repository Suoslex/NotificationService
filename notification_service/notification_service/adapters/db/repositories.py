from uuid import UUID

from loguru import logger

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
        logger.debug(f"Checking if notification exists with UUID: {uuid}")
        exists = NotificationModel.objects.filter(uuid=uuid).exists()
        logger.debug(f"Notification with UUID {uuid} exists: {exists}")
        return exists

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
        logger.debug(f"Fetching notification by UUID: {uuid}")
        obj = NotificationModel.objects.filter(uuid=uuid).first()
        if not obj:
            logger.warning(f"Notification with UUID {uuid} not found")
            raise ObjectNotFoundInRepository()
        notification = self._model_to_entity(obj)
        logger.debug(f"Fetched notification: {notification}")
        return notification

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
        logger.debug(f"Creating new notification: {notification.uuid}")
        notification_model = NotificationModel.objects.create(
            uuid=notification.uuid,
            user_uuid=notification.user_uuid,
            title=notification.title,
            text=notification.text,
            type=notification.type,
        )
        result = self._model_to_entity(notification_model)
        logger.debug(f"Created notification: {result}")
        return result

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
        logger.debug(f"Updating notification: {notification.uuid}")
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
            logger.warning(
                f"Failed to update notification "
                f"{notification.uuid}, not found"
            )
            raise ObjectNotFoundInRepository()
        logger.debug(f"Updated notification: {notification}")
        return notification

    def get_pending_for_update(self) -> Notification | None:
        """
        Get pending notification for update,
        locking a row while transaction is alive.

        Returns
        ----------
        Notification | None
            Notification object or None, if there are no pending notifications 
        """
        logger.debug("Fetching pending notification for update")
        obj = (
            NotificationModel.objects
            .select_for_update(skip_locked=True)
            .filter(status=NotificationStatus.PENDING)
            .order_by("created_at")
            .first()
        )
        result = self._model_to_entity(obj) if obj else None
        if result:
            logger.debug(f"Fetched pending notification: {result.uuid}")
        else:
            logger.debug("No pending notifications found")
        return result

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