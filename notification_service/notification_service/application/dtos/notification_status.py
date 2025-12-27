from uuid import UUID
from dataclasses import dataclass

from notification_service.domain.enums import NotificationStatus


@dataclass(frozen=True)
class NotificationStatusDTO:
    """
    Data transfer object for notification status.

    Contains information about the status of a notification.
    """
    uuid: UUID
    status: NotificationStatus
    was_created: bool
