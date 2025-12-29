"""Tests for domain enums."""

import pytest

from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus,
)


class TestNotificationType:
    """Tests for NotificationType enum."""

    def test_notification_type_values(self):
        """Test that NotificationType has correct values."""
        assert NotificationType.EMAIL == "email"
        assert NotificationType.SMS == "sms"
        assert NotificationType.PUSH == "push"
        assert NotificationType.TELEGRAM == "telegram"
        assert isinstance(NotificationType.EMAIL, str)

    def test_notification_type_membership(self):
        """Test membership checks."""
        assert NotificationType.EMAIL in NotificationType
        assert NotificationType("email") == NotificationType.EMAIL
        assert NotificationType("email") in NotificationType
        with pytest.raises(ValueError):
            NotificationType("invalid")

    def test_notification_type_iteration(self):
        """Test iterating over NotificationType."""
        types = list(NotificationType)
        assert len(types) == 4
        assert NotificationType.EMAIL in types
        assert NotificationType.SMS in types
        assert NotificationType.PUSH in types
        assert NotificationType.TELEGRAM in types


class TestNotificationStatus:
    """Tests for NotificationStatus enum."""

    def test_notification_status_values(self):
        """Test that NotificationStatus has correct values."""
        assert NotificationStatus.PENDING == "pending"
        assert NotificationStatus.SENT == "sent"
        assert NotificationStatus.FAILED == "failed"

    def test_notification_status_membership(self):
        """Test membership checks."""
        assert NotificationStatus.PENDING in NotificationStatus
        assert NotificationStatus("pending") == NotificationStatus.PENDING
        assert NotificationStatus("pending") in NotificationStatus
        with pytest.raises(ValueError):
            NotificationStatus("invalid")

    def test_notification_status_iteration(self):
        """Test iterating over NotificationStatus."""
        statuses = list(NotificationStatus)
        assert len(statuses) == 3
        assert NotificationStatus.PENDING in statuses
        assert NotificationStatus.SENT in statuses
        assert NotificationStatus.FAILED in statuses
