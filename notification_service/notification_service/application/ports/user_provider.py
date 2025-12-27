from abc import ABC, abstractmethod

from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings
)


class UserProviderPort(ABC):
    """
    Abstract base class for user provider port.
    Defines the interface for user-related operations.
    """
    @abstractmethod
    def get_notification_settings(
            self,
            user_id: int
    ) -> UserNotificationsSettings:
        """
        Get notification settings for a user.

        Parameters
        ----------
        user_id : int
            ID of the user

        Returns
        ----------
        UserNotificationsSettings
            Notification settings for the user
        """
        ...
