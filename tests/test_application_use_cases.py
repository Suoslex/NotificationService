"""Tests for application use cases."""

from uuid import uuid4
from unittest.mock import Mock

import pytest

from notification_service.application.use_cases.send_notification import (
    SendNotificationUseCase,
)
from notification_service.domain.entities import Notification
from notification_service.domain.enums import (
    NotificationStatus,
    NotificationType,
)
from notification_service.application.dtos.notification_status import (
    NotificationStatusDTO,
)



class TestSendNotificationUseCase:
    """Tests for SendNotificationUseCase."""

    @pytest.fixture
    def mock_uow(self):
        """Create a mock unit of work."""
        uow = Mock()
        uow.notification_repo = Mock()
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=None)
        return uow

    @pytest.fixture
    def use_case(self, mock_uow):
        """Create a SendNotificationUseCase instance."""
        return SendNotificationUseCase(mock_uow)

    @pytest.fixture
    def notification(self):
        """Create a test notification."""
        return Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

    def test_execute_new_notification(self, use_case, mock_uow, notification):
        """Test executing use case for a new notification."""
        mock_uow.notification_repo.exists.return_value = False
        mock_uow.notification_repo.create.return_value = notification

        result = use_case.execute(notification)

        assert isinstance(result, NotificationStatusDTO)
        assert result.uuid == notification.uuid
        assert result.status == notification.status
        assert result.was_created is True
        mock_uow.notification_repo.exists.assert_called_once_with(
            notification.uuid
        )
        mock_uow.notification_repo.create.assert_called_once_with(notification)

    def test_execute_existing_notification(
        self, use_case, mock_uow, notification
    ):
        """Test executing use case for an existing notification."""
        existing_notification = Notification(
            uuid=notification.uuid,
            user_uuid=notification.user_uuid,
            title="Existing Title",
            text="Existing Text",
            status=NotificationStatus.SENT,
        )
        mock_uow.notification_repo.exists.return_value = True
        mock_uow.notification_repo.get_by_uuid.return_value = (
            existing_notification
        )

        result = use_case.execute(notification)

        assert isinstance(result, NotificationStatusDTO)
        assert result.uuid == existing_notification.uuid
        assert result.status == existing_notification.status
        assert result.was_created is False
        mock_uow.notification_repo.exists.assert_called_once_with(
            notification.uuid
        )
        mock_uow.notification_repo.get_by_uuid.assert_called_once_with(
            notification.uuid
        )
        mock_uow.notification_repo.create.assert_not_called()

    def test_execute_uses_context_manager(
        self, use_case, mock_uow, notification
    ):
        """Test that use case uses unit of work as context manager."""
        mock_uow.notification_repo.exists.return_value = False
        mock_uow.notification_repo.create.return_value = notification

        use_case.execute(notification)

        mock_uow.__enter__.assert_called_once()
        mock_uow.__exit__.assert_called_once()

    def test_execute_with_none_type(self, use_case, mock_uow):
        """Test executing use case with notification type None."""
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=None,
        )
        mock_uow.notification_repo.exists.return_value = False
        mock_uow.notification_repo.create.return_value = notification

        result = use_case.execute(notification)

        assert result.uuid == notification.uuid
        assert result.was_created is True

