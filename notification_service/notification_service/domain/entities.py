from uuid import UUID
from dataclasses import dataclass

from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus
)

@dataclass
class Notification:
    uuid: UUID
    user_id: int
    title: str
    text: str
    type: NotificationType | None = None
    status: NotificationStatus = NotificationStatus.PENDING
