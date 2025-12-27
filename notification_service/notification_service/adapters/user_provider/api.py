from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings
)
from notification_service.application.ports.user_provider import (
    UserProviderPort
)


class APIUserProvider(UserProviderPort):
    def get_notification_settings(
            self,
            user_id: int
    ) -> UserNotificationsSettings:
        ...