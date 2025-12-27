from abc import ABC, abstractmethod
from uuid import UUID

from notification_service.domain.entities import Notification


class NotificationRepositoryPort(ABC):
    """
    Abstract base class for notification repository port.
    Defines the interface for notification repository operations.
    """
    @abstractmethod
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
            True if notification exists, False otherwise.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        """
        ...

    @abstractmethod
    def get_by_uuid(self, uuid: UUID) -> Notification | None:
        """
        Get notification by its UUID.

        Parameters
        ----------
        uuid : UUID
            UUID of the notification

        Returns
        ----------
        Notification or None
            Notification object or None if not found
        """
        ...

    @abstractmethod
    def get_pending_for_update(self) -> Notification | None:
        """
        Get pending notification for update, locking a row while transaction is alive.

        Returns
        ----------
        Notification or None
            Notification object or None if no pending notifications
        """
        ...

