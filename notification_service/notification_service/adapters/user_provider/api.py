from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings
)
from notification_service.application.ports.user_provider import (
    UserProviderPort
)


class APIUserProvider(UserProviderPort):
    """
    API-based user provider.

    Provides user notification settings by fetching from external API.
    """
    def get_notification_settings(
            self,
            user_id: int
    ) -> UserNotificationsSettings:
        """
        Get notification settings for a user from external API.

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