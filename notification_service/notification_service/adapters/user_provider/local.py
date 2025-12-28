from uuid import UUID

from loguru import logger

from notification_service.domain.enums import NotificationType
from notification_service.application.ports.exceptions.user_provider import (
    UserNotFound
)
from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings
)
from notification_service.application.ports.user_provider import (
    UserProviderPort
)


class LocalUserProvider(UserProviderPort):
    """
    Local user provider.

    Provides user notification settings from local storage.
    """
    def get_notification_settings(
            self,
            user_uuid: UUID
    ) -> UserNotificationsSettings:
        """
        Get notification settings for a user from local storage.

        Parameters
        ----------
        user_uuid : UUID
            UUID of the user

        Returns
        ----------
        UserNotificationsSettings
            Notification settings for the user

        Raises
        ----------
        UserNotFound
            If user is not found in local storage
        """
        logger.debug(
            f"Fetching notification settings for user {user_uuid} "
            "from local storage"
        )
        if user_uuid not in self._local_users:
            logger.warning(f"User {user_uuid} not found in local storage")
            raise UserNotFound()
        settings = self._local_users[user_uuid]
        logger.debug(
            f"Retrieved notification settings "
            f"for user {user_uuid}: {settings}"
        )
        return settings

    _local_users = {
        UUID("00000000-0000-0000-0000-000000000000"): (
            UserNotificationsSettings(
                user_uuid=UUID("00000000-0000-0000-0000-000000000000"),
                notification_channels={
                    NotificationType.EMAIL: "example@localhost",
                    NotificationType.PUSH: "392301"
                },
                preferred_notification_channel=NotificationType.EMAIL
            )
        ),
        UUID("00000000-0000-0000-0000-000000000001"): (
            UserNotificationsSettings(
                user_uuid=UUID("00000000-0000-0000-0000-000000000001"),
                notification_channels={
                    NotificationType.SMS: "+000000000001",
                    NotificationType.PUSH: "392302",
                    NotificationType.EMAIL: "example2@localhost",
                },
                preferred_notification_channel=NotificationType.PUSH
            )
        ),
    }
