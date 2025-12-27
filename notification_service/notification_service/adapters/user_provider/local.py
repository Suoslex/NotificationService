from notification_service.domain.enums import NotificationType
from notification_service.application.ports.exceptions import UserNotFound
from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings
)
from notification_service.application.ports.user_provider import (
    UserProviderPort
)


class LocalUserProvider(UserProviderPort):
    def get_notification_settings(
            self,
            user_id: int
    ) -> UserNotificationsSettings:
        if user_id not in self._local_users:
            raise UserNotFound()
        return self._local_users[user_id]

    _local_users = {
        1: UserNotificationsSettings(
            user_id=1,
            notification_channels={
                NotificationType.EMAIL: "example@localhost",
                NotificationType.PUSH: "392301"
            },
            preferred_notification_channel=NotificationType.EMAIL
        ),
        2: UserNotificationsSettings(
            user_id=2,
            notification_channels={
                NotificationType.SMS: "+000000000001",
                NotificationType.PUSH: "392302",
                NotificationType.EMAIL: "example2@localhost",
            },
            preferred_notification_channel=NotificationType.PUSH
        ),
    }