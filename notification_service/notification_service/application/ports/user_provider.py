from abc import ABC, abstractmethod

from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings
)


class UserProviderPort(ABC):
    @abstractmethod
    def get_notification_settings(
            self,
            user_id: int
    ) -> UserNotificationsSettings: ...
