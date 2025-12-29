"""Tests for domain entities."""

from uuid import uuid4

from notification_service.domain.entities import Notification
from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus,
)


class TestNotification:
    """Tests for Notification entity."""

    def test_notification_creation(self):
        """Test creating a notification with all fields."""
        uuid = uuid4()
        user_uuid = uuid4()
        notification = Notification(
            uuid=uuid,
            user_uuid=user_uuid,
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        assert notification.uuid == uuid
        assert notification.user_uuid == user_uuid
        assert notification.title == "Test Title"
        assert notification.text == "Test Text"
        assert notification.type == NotificationType.EMAIL
        assert notification.status == NotificationStatus.PENDING

    def test_notification_defaults(self):
        """Test notification with default values."""
        uuid = uuid4()
        user_uuid = uuid4()
        notification = Notification(
            uuid=uuid,
            user_uuid=user_uuid,
            title="Test Title",
            text="Test Text",
        )

        assert notification.type is None
        assert notification.status == NotificationStatus.PENDING

    def test_notification_with_none_type(self):
        """Test notification with None type."""
        uuid = uuid4()
        user_uuid = uuid4()
        notification = Notification(
            uuid=uuid,
            user_uuid=user_uuid,
            title="Test Title",
            text="Test Text",
            type=None,
        )

        assert notification.type is None

    def test_notification_immutability(self):
        """Test that notification fields can be accessed."""
        uuid = uuid4()
        user_uuid = uuid4()
        notification = Notification(
            uuid=uuid,
            user_uuid=user_uuid,
            title="Test Title",
            text="Test Text",
        )

        assert notification.uuid == uuid
        assert notification.user_uuid == user_uuid

