"""Tests for user provider adapters."""

from uuid import UUID, uuid4
from unittest.mock import patch

import pytest
from keycloak.exceptions import (
    KeycloakGetError,
    KeycloakError,
    KeycloakConnectionError,
)

from notification_service.adapters.user_provider.local import LocalUserProvider
from notification_service.adapters.user_provider.keycloak import (
    KeycloakUserProvider,
)
from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings,
)
from notification_service.domain.enums import NotificationType
from notification_service.application.ports.exceptions.user_provider import (
    UserNotFound,
)
from notification_service.application.ports.exceptions.base import (
    TemporaryFailure,
)


class TestLocalUserProvider:
    """Tests for LocalUserProvider."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return LocalUserProvider()

    def test_get_notification_settings_existing_user(self, provider):
        """Test getting notification settings for existing user."""
        user_uuid = UUID("00000000-0000-0000-0000-000000000000")

        settings = provider.get_notification_settings(user_uuid)

        assert isinstance(settings, UserNotificationsSettings)
        assert settings.user_uuid == user_uuid
        assert NotificationType.EMAIL in settings.notification_channels
        assert NotificationType.PUSH in settings.notification_channels
        assert (
            settings.preferred_notification_channel == NotificationType.EMAIL
        )

    def test_get_notification_settings_another_user(self, provider):
        """Test getting notification settings for another existing user."""
        user_uuid = UUID("00000000-0000-0000-0000-000000000001")

        settings = provider.get_notification_settings(user_uuid)

        assert isinstance(settings, UserNotificationsSettings)
        assert settings.user_uuid == user_uuid
        assert NotificationType.SMS in settings.notification_channels
        assert NotificationType.PUSH in settings.notification_channels
        assert NotificationType.EMAIL in settings.notification_channels
        assert settings.preferred_notification_channel == NotificationType.PUSH

    def test_get_notification_settings_user_not_found(self, provider):
        """Test getting notification settings for non-existing user."""
        user_uuid = uuid4()

        with pytest.raises(UserNotFound):
            provider.get_notification_settings(user_uuid)


class TestKeycloakUserProvider:
    """Tests for KeycloakUserProvider."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return KeycloakUserProvider()

    @patch(
        "notification_service.adapters.user_provider.keycloak.keycloak_admin"
    )
    def test_get_notification_settings_success(
        self, mock_keycloak_admin, provider
    ):
        """Test getting notification settings successfully from Keycloak."""
        user_uuid = uuid4()
        user_data = {
            "id": str(user_uuid),
            "attributes": {
                "email": ["test@example.com"],
                "sms": ["+1234567890"],
                "preferred_notification_channel": ["email"],
            },
        }
        mock_keycloak_admin.get_user.return_value = user_data

        settings = provider.get_notification_settings(user_uuid)

        assert isinstance(settings, UserNotificationsSettings)
        assert settings.user_uuid == user_uuid
        assert NotificationType.EMAIL in settings.notification_channels
        assert NotificationType.SMS in settings.notification_channels
        mock_keycloak_admin.get_user.assert_called_once_with(str(user_uuid))

    @patch(
        "notification_service.adapters.user_provider.keycloak.keycloak_admin"
    )
    def test_get_notification_settings_user_not_found(
        self, mock_keycloak_admin, provider
    ):
        """
        Test getting notification settings
        when user not found in Keycloak.
        """
        user_uuid = uuid4()
        mock_keycloak_admin.get_user.side_effect = KeycloakGetError(
            "User not found"
        )

        with pytest.raises(UserNotFound):
            provider.get_notification_settings(user_uuid)

    @patch(
        "notification_service.adapters.user_provider.keycloak.keycloak_admin"
    )
    def test_get_notification_settings_connection_error(
        self, mock_keycloak_admin, provider
    ):
        """
        Test getting notification settings when Keycloak connection fails.
        """
        user_uuid = uuid4()
        mock_keycloak_admin.get_user.side_effect = KeycloakConnectionError(
            "Connection failed"
        )

        with pytest.raises(TemporaryFailure):
            provider.get_notification_settings(user_uuid)

    @patch(
        "notification_service.adapters.user_provider.keycloak.keycloak_admin"
    )
    def test_get_notification_settings_keycloak_error(
        self, mock_keycloak_admin, provider
    ):
        """Test getting notification settings when Keycloak error occurs."""
        user_uuid = uuid4()
        mock_keycloak_admin.get_user.side_effect = KeycloakError(
            "Keycloak error"
        )

        with pytest.raises(TemporaryFailure):
            provider.get_notification_settings(user_uuid)

    @patch(
        "notification_service.adapters.user_provider.keycloak.keycloak_admin"
    )
    def test_get_notification_settings_no_attributes(
        self, mock_keycloak_admin, provider
    ):
        """Test getting notification settings when user has no attributes."""
        user_uuid = uuid4()
        user_data = {"id": str(user_uuid), "attributes": {}}
        mock_keycloak_admin.get_user.return_value = user_data

        settings = provider.get_notification_settings(user_uuid)

        assert isinstance(settings, UserNotificationsSettings)
        assert settings.user_uuid == user_uuid
        assert len(settings.notification_channels) == 0
        assert settings.preferred_notification_channel is None
