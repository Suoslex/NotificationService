from uuid import UUID
from dataclasses import dataclass

from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus
)

@dataclass
class Notification:
    """
    Notification entity.
    Represents a notification with its properties and status.
    """
    uuid: UUID
    user_uuid: UUID
    title: str
    text: str
    type: NotificationType | None = None
    status: NotificationStatus = NotificationStatus.PENDING
