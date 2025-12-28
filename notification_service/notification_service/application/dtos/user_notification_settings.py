from uuid import UUID
from dataclasses import dataclass

from notification_service.domain.enums import NotificationType


@dataclass(frozen=True)
class UserNotificationsSettings:
    """
    Data transfer object for user notification settings.

    Contains information about user's notification preferences and channels.
    """
    user_uuid: UUID
    notification_channels: dict[NotificationType, str]
    preferred_notification_channel: NotificationType
