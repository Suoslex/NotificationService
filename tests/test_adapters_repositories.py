"""Tests for adapter repositories."""

from uuid import uuid4

import pytest

from notification_service.adapters.db.repositories import (
    DjangoNotificationRepository,
)
from notification_service.domain.entities import Notification
from notification_service.domain.enums import (
    NotificationStatus,
    NotificationType,
)
from notification_service.application.ports.exceptions.repository import (
    ObjectNotFoundInRepository,
)


@pytest.mark.django_db
class TestDjangoNotificationRepository:
    """Tests for DjangoNotificationRepository."""

    def test_initialization(self):
        """Test repository initialization."""
        repo = DjangoNotificationRepository()

        assert repo is not None

    def test_exists_found(self):
        """Test exists method when notification exists."""
        repo = DjangoNotificationRepository()
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test",
            text="Test text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        repo.create(notification)
        result = repo.exists(notification.uuid)

        assert result is True

    def test_exists_not_found(self):
        """Test exists method when notification does not exist."""
        repo = DjangoNotificationRepository()
        fake_uuid = uuid4()

        result = repo.exists(fake_uuid)

        assert result is False

    def test_get_by_uuid_success(self):
        """Test get_by_uuid method for existing notification."""
        repo = DjangoNotificationRepository()
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test",
            text="Test text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        created = repo.create(notification)
        retrieved = repo.get_by_uuid(created.uuid)

        assert retrieved.uuid == created.uuid
        assert retrieved.user_uuid == created.user_uuid
        assert retrieved.title == created.title
        assert retrieved.text == created.text
        assert retrieved.type == created.type
        assert retrieved.status == created.status

    def test_get_by_uuid_not_found(self):
        """Test get_by_uuid method when notification does not exist."""
        repo = DjangoNotificationRepository()
        fake_uuid = uuid4()

        with pytest.raises(ObjectNotFoundInRepository):
            repo.get_by_uuid(fake_uuid)

    def test_create_success(self):
        """Test create method."""
        repo = DjangoNotificationRepository()
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test",
            text="Test text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        created = repo.create(notification)

        assert created.uuid == notification.uuid
        assert created.user_uuid == notification.user_uuid
        assert created.title == notification.title
        assert created.text == notification.text
        assert created.type == notification.type
        assert created.status == notification.status

    def test_update_success(self):
        """Test update method."""
        repo = DjangoNotificationRepository()
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test",
            text="Test text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        created = repo.create(notification)
        updated_notification = Notification(
            uuid=created.uuid,
            user_uuid=created.user_uuid,
            title="Updated",
            text="Updated text",
            type=NotificationType.SMS,
            status=NotificationStatus.SENT,
        )

        updated = repo.update(updated_notification)

        assert updated.uuid == created.uuid
        assert updated.title == "Updated"
        assert updated.text == "Updated text"
        assert updated.type == NotificationType.SMS
        assert updated.status == NotificationStatus.SENT

    def test_update_not_found(self):
        """Test update method when notification does not exist."""
        repo = DjangoNotificationRepository()
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test",
            text="Test text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        with pytest.raises(ObjectNotFoundInRepository):
            repo.update(notification)

    def test_get_pending_for_update_found(self):
        """
        Test get_pending_for_update method
        when pending notification exists.
        """
        repo = DjangoNotificationRepository()
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test",
            text="Test text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        repo.create(notification)
        result = repo.get_pending_for_update()

        assert result is not None
        assert result.uuid == notification.uuid
        assert result.status == NotificationStatus.PENDING

    def test_get_pending_for_update_not_found(self):
        """
        Test get_pending_for_update method
        when no pending notifications exist.
        """
        repo = DjangoNotificationRepository()

        result = repo.get_pending_for_update()

        assert result is None
