from uuid import UUID
from dataclasses import dataclass

from notification_service.domain.enums import NotificationStatus


@dataclass(frozen=True)
class NotificationStatusDTO:
    uuid: UUID
    status: NotificationStatus
    was_created: bool
