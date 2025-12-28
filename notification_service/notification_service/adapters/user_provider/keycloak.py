from uuid import UUID

from keycloak.exceptions import (
    KeycloakError,
    KeycloakGetError,
    KeycloakConnectionError
)
from loguru import logger

from notification_service.domain.enums import NotificationType
from notification_service.application.ports.exceptions.base import (
    TemporaryFailure
)
from notification_service.application.ports.exceptions.user_provider import (
    UserNotFound
)
from notification_service.config.keycloak import keycloak_admin
from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings
)
from notification_service.application.ports.user_provider import (
    UserProviderPort
)


class KeycloakUserProvider(UserProviderPort):
    """
    Keycloak user provider.

    Provides user notification settings by fetching from Keycloak.
    """
    def get_notification_settings(
            self,
            user_uuid: UUID
    ) -> UserNotificationsSettings:
        """
        Get notification settings for a user from Keycloak.

        Parameters
        ----------
        user_uuid : UUID
            UUID of the user

        Returns
        ----------
        UserNotificationsSettings
            Notification settings for the user
        """
        logger.debug(
            f"Fetching notification settings for user {user_uuid} "
            "from Keycloak"
        )
        try:
            user_data = keycloak_admin.get_user(str(user_uuid))
            logger.debug(
                f"Successfully retrieved user data for {user_uuid} "
                f"from Keycloak: {user_data}"
            )
        except KeycloakGetError:
            logger.warning(f"User {user_uuid} not found in Keycloak")
            raise UserNotFound(f"User {user_uuid} not found in Keycloak")
        except (KeycloakError, KeycloakConnectionError) as e:
            logger.error(
                f"Couldn't connect to Keycloak "
                f"server for user {user_uuid}: {e}"
            )
            raise TemporaryFailure("Cannot connect to Keycloak server")

        attributes = user_data.get("attributes", {})
        logger.debug(
            f"Retrieved attributes for user {user_uuid}: "
            f"{list(attributes.keys())}"
        )

        channels = {
            notification_type: attributes[notification_type][0]
            for notification_type in NotificationType
            if notification_type in attributes
        }
        logger.debug(
            f"Processed notification channels for user {user_uuid}: {channels}"
        )

        settings = UserNotificationsSettings(
            user_uuid=user_uuid,
            notification_channels=channels,
            preferred_notification_channel=attributes.get(
                "preferred_notification_channel"
            )
        )
        logger.debug(
            f"Created notification settings for user {user_uuid}: {settings}"
        )
        return settings