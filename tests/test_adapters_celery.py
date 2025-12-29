"""Tests for Celery tasks."""

from uuid import uuid4

import pytest
from unittest.mock import Mock, patch

from notification_service.adapters.workers.celery import send_notifications
from notification_service.domain.entities import Notification
from notification_service.domain.enums import (
    NotificationStatus,
    NotificationType,
)
from notification_service.application.ports.exceptions.user_provider import (
    UserNotFound,
)
from notification_service.application.ports.exceptions.workers import (
    NotificationChannelError,
)
from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings,
)


@pytest.mark.django_db
class TestSendNotificationsTask:
    """Tests for send_notifications Celery task."""

    @patch("notification_service.adapters.workers.celery.get_unit_of_work")
    @patch("notification_service.adapters.workers.celery.get_user_provider")
    def test_send_notifications_no_pending(
        self, mock_get_user_provider, mock_get_uow
    ):
        """Test task when there are no pending notifications."""
        mock_uow = Mock()
        mock_uow.notification_repo = Mock()
        mock_uow.notification_repo.get_pending_for_update.return_value = None
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)
        mock_get_uow.return_value = mock_uow

        mock_provider = Mock()
        mock_get_user_provider.return_value = mock_provider

        send_notifications()

        mock_uow.notification_repo.get_pending_for_update.assert_called_once()
        mock_provider.get_notification_settings.assert_not_called()

    @patch("notification_service.adapters.workers.celery.get_unit_of_work")
    @patch("notification_service.adapters.workers.celery.get_user_provider")
    @patch(
        "notification_service.adapters.workers.celery.get_notification_channel"
    )
    def test_send_notifications_success(
        self, mock_get_channel, mock_get_user_provider, mock_get_uow
    ):
        """Test successful notification sending."""
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={NotificationType.EMAIL: "test@example.com"},
            preferred_notification_channel=NotificationType.EMAIL,
        )

        mock_uow = Mock()
        mock_uow.notification_repo = Mock()
        mock_uow.notification_repo.get_pending_for_update.return_value = (
            notification
        )
        mock_uow.notification_repo.update = Mock()
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)
        mock_get_uow.return_value = mock_uow

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_channel = Mock()
        mock_get_channel.return_value = mock_channel

        send_notifications()

        mock_uow.notification_repo.get_pending_for_update.assert_called_once()
        mock_provider.get_notification_settings.assert_called_once_with(
            user_uuid=notification.user_uuid
        )
        mock_get_channel.assert_called_once_with(NotificationType.EMAIL)
        mock_channel.send.assert_called_once_with(notification)
        mock_uow.notification_repo.update.assert_called_once()
        updated_notification = (
            mock_uow.notification_repo.update.call_args[0][0]
        )
        assert updated_notification.status == NotificationStatus.SENT

    @patch("notification_service.adapters.workers.celery.get_unit_of_work")
    @patch("notification_service.adapters.workers.celery.get_user_provider")
    def test_send_notifications_user_not_found(
        self, mock_get_user_provider, mock_get_uow
    ):
        """Test notification sending when user is not found."""
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        mock_uow = Mock()
        mock_uow.notification_repo = Mock()
        mock_uow.notification_repo.get_pending_for_update.return_value = (
            notification
        )
        mock_uow.notification_repo.update = Mock()
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)
        mock_get_uow.return_value = mock_uow

        mock_provider = Mock()
        mock_provider.get_notification_settings.side_effect = UserNotFound()
        mock_get_user_provider.return_value = mock_provider

        send_notifications()

        mock_uow.notification_repo.update.assert_called_once()
        updated_notification = (
            mock_uow.notification_repo.update.call_args[0][0]
        )
        assert updated_notification.status == NotificationStatus.FAILED

    @patch("notification_service.adapters.workers.celery.get_unit_of_work")
    @patch("notification_service.adapters.workers.celery.get_user_provider")
    def test_send_notifications_user_doesnt_have_channel(
        self, mock_get_user_provider, mock_get_uow
    ):
        """Test notification sending when user doesn't have required channel"""
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={NotificationType.SMS: "+1234567890"},
            preferred_notification_channel=NotificationType.SMS,
        )

        mock_uow = Mock()
        mock_uow.notification_repo = Mock()
        mock_uow.notification_repo.get_pending_for_update.return_value = (
            notification
        )
        mock_uow.notification_repo.update = Mock()
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)
        mock_get_uow.return_value = mock_uow

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        send_notifications()

        mock_uow.notification_repo.update.assert_called_once()
        updated_notification = (
            mock_uow.notification_repo.update.call_args[0][0]
        )
        assert updated_notification.status == NotificationStatus.FAILED

    @patch("notification_service.adapters.workers.celery.get_unit_of_work")
    @patch("notification_service.adapters.workers.celery.get_user_provider")
    @patch(
        "notification_service.adapters.workers.celery.get_notification_channel"
    )
    def test_send_notifications_channel_error(
        self, mock_get_channel, mock_get_user_provider, mock_get_uow
    ):
        """Test notification sending when channel raises error."""
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={
                NotificationType.EMAIL: "test@example.com",
                NotificationType.SMS: "+1234567890",
            },
            preferred_notification_channel=NotificationType.EMAIL,
        )

        mock_uow = Mock()
        mock_uow.notification_repo = Mock()
        mock_uow.notification_repo.get_pending_for_update.return_value = (
            notification
        )
        mock_uow.notification_repo.update = Mock()
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)
        mock_get_uow.return_value = mock_uow

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_channel = Mock()
        mock_channel.send.side_effect = NotificationChannelError(
            "Channel error"
        )
        mock_get_channel.return_value = mock_channel

        send_notifications()

        assert mock_uow.notification_repo.update.called
        updated_notification = (
            mock_uow.notification_repo.update.call_args[0][0]
        )
        assert updated_notification.status == NotificationStatus.FAILED

    @patch("notification_service.adapters.workers.celery.get_unit_of_work")
    @patch("notification_service.adapters.workers.celery.get_user_provider")
    @patch(
        "notification_service.adapters.workers.celery.get_notification_channel"
    )
    def test_send_notifications_no_type_uses_preferred(
        self, mock_get_channel, mock_get_user_provider, mock_get_uow
    ):
        """Test notification sending without type uses preferred channel."""
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=None,
            status=NotificationStatus.PENDING,
        )

        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={
                NotificationType.EMAIL: "test@example.com",
                NotificationType.SMS: "+1234567890",
            },
            preferred_notification_channel=NotificationType.EMAIL,
        )

        mock_uow = Mock()
        mock_uow.notification_repo = Mock()
        mock_uow.notification_repo.get_pending_for_update.return_value = (
            notification
        )
        mock_uow.notification_repo.update = Mock()
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)
        mock_get_uow.return_value = mock_uow

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_channel = Mock()
        mock_get_channel.return_value = mock_channel

        send_notifications()

        assert mock_get_channel.called
        assert mock_get_channel.call_args[0][0] == NotificationType.EMAIL
        assert mock_channel.send.called

    @patch("notification_service.adapters.workers.celery.get_unit_of_work")
    @patch("notification_service.adapters.workers.celery.get_user_provider")
    @patch(
        "notification_service.adapters.workers.celery.get_notification_channel"
    )
    def test_send_notifications_channel_unexpected_exception(
        self, mock_get_channel, mock_get_user_provider, mock_get_uow
    ):
        """Test notification sending when channel raises unexpected error."""
        notification = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.SMS,
            status=NotificationStatus.PENDING,
        )

        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={
                NotificationType.EMAIL: "test@example.com",
                NotificationType.SMS: "+1234567890",
            },
            preferred_notification_channel=NotificationType.EMAIL,
        )

        mock_uow = Mock()
        mock_uow.notification_repo = Mock()
        mock_uow.notification_repo.get_pending_for_update.return_value = (
            notification
        )
        mock_uow.notification_repo.update = Mock()
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)
        mock_get_uow.return_value = mock_uow

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_channel = Mock()
        mock_channel.send.side_effect = ValueError("Unexpected error")
        mock_get_channel.return_value = mock_channel

        send_notifications()

        assert mock_get_channel.call_args[0][0] == NotificationType.SMS
        assert mock_uow.notification_repo.update.called
        updated_notification = (
            mock_uow.notification_repo.update.call_args[0][0]
        )
        assert updated_notification.status == NotificationStatus.FAILED
