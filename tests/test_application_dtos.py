"""Tests for application DTOs."""

from uuid import uuid4

import pytest

from notification_service.application.dtos.notification_status import (
    NotificationStatusDTO,
)
from notification_service.application.dtos.auth_context import AuthContext
from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings,
)
from notification_service.domain.enums import (
    NotificationStatus,
    NotificationType,
)


class TestNotificationStatusDTO:
    """Tests for NotificationStatusDTO."""

    def test_notification_status_dto_creation(self):
        """Test creating a NotificationStatusDTO."""
        uuid = uuid4()
        dto = NotificationStatusDTO(
            uuid=uuid, status=NotificationStatus.PENDING, was_created=True
        )

        assert dto.uuid == uuid
        assert dto.status == NotificationStatus.PENDING
        assert dto.was_created is True

    def test_notification_status_dto_immutability(self):
        """Test that DTO is frozen (immutable)."""
        from dataclasses import FrozenInstanceError

        uuid = uuid4()
        dto = NotificationStatusDTO(
            uuid=uuid, status=NotificationStatus.SENT, was_created=False
        )

        with pytest.raises(FrozenInstanceError):
            dto.was_created = True


class TestAuthContext:
    """Tests for AuthContext."""

    def test_auth_context_creation(self):
        """Test creating an AuthContext."""
        user_uuid = uuid4()
        scopes = {"read", "write"}
        auth_context = AuthContext(user_uuid=user_uuid, scopes=scopes)

        assert auth_context.user_uuid == user_uuid
        assert auth_context.scopes == scopes

    def test_auth_context_has_scope(self):
        """Test has() method for scope checking."""
        user_uuid = uuid4()
        scopes = {"read", "write", "admin"}
        auth_context = AuthContext(user_uuid=user_uuid, scopes=scopes)

        assert auth_context.has("read") is True
        assert auth_context.has("write") is True
        assert auth_context.has("admin") is True
        assert auth_context.has("delete") is False

    def test_auth_context_immutability(self):
        """Test that AuthContext is frozen."""
        from dataclasses import FrozenInstanceError

        user_uuid = uuid4()
        auth_context = AuthContext(user_uuid=user_uuid, scopes={"read"})

        with pytest.raises(FrozenInstanceError):
            auth_context.scopes = {"write"}


class TestUserNotificationsSettings:
    """Tests for UserNotificationsSettings."""

    def test_user_notifications_settings_creation(self):
        """Test creating UserNotificationsSettings."""
        user_uuid = uuid4()
        channels = {
            NotificationType.EMAIL: "test@example.com",
            NotificationType.SMS: "+1234567890",
        }
        settings = UserNotificationsSettings(
            user_uuid=user_uuid,
            notification_channels=channels,
            preferred_notification_channel=NotificationType.EMAIL,
        )

        assert settings.user_uuid == user_uuid
        assert settings.notification_channels == channels
        assert (
            settings.preferred_notification_channel == NotificationType.EMAIL
        )

    def test_user_notifications_settings_without_preferred(self):
        """Test UserNotificationsSettings without preferred channel."""
        user_uuid = uuid4()
        channels = {NotificationType.PUSH: "token123"}
        settings = UserNotificationsSettings(
            user_uuid=user_uuid,
            notification_channels=channels,
            preferred_notification_channel=None,
        )

        assert settings.preferred_notification_channel is None

    def test_user_notifications_settings_immutability(self):
        """Test that UserNotificationsSettings is frozen."""
        from dataclasses import FrozenInstanceError

        user_uuid = uuid4()
        settings = UserNotificationsSettings(
            user_uuid=user_uuid,
            notification_channels={NotificationType.EMAIL: "test@example.com"},
            preferred_notification_channel=NotificationType.EMAIL,
        )

        with pytest.raises(FrozenInstanceError):
            settings.preferred_notification_channel = NotificationType.SMS
