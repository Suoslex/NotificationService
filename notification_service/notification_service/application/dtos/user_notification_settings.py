from dataclasses import dataclass

from notification_service.domain.enums import NotificationType


@dataclass(frozen=True)
class UserNotificationsSettings:
    user_id: int
    notification_channels: dict[NotificationType, str]
    preferred_notification_channel: NotificationType
