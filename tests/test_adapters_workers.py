"""Tests for worker adapters."""

import smtplib
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock

import pytest
from requests.exceptions import RequestException

from notification_service.adapters.workers.notification_channels import (
    get_notification_channel,
    EmailNotificationChannel,
    SMSNotificationChannel,
    PushNotificationChannel,
    TelegramNotificationChannel,
)
from notification_service.domain.entities import Notification
from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus,
)
from notification_service.application.ports.exceptions.workers import (
    UserDoesntHaveTheChannel,
    CouldntSendNotification,
)
from notification_service.application.dtos.user_notification_settings import (
    UserNotificationsSettings,
)


class TestGetNotificationChannel:
    """Tests for get_notification_channel function."""

    def test_get_email_channel(self):
        """Test getting email notification channel."""
        channel = get_notification_channel(NotificationType.EMAIL)
        assert isinstance(channel, EmailNotificationChannel)

    def test_get_sms_channel(self):
        """Test getting SMS notification channel."""
        channel = get_notification_channel(NotificationType.SMS)
        assert isinstance(channel, SMSNotificationChannel)

    def test_get_push_channel(self):
        """Test getting push notification channel."""
        channel = get_notification_channel(NotificationType.PUSH)
        assert isinstance(channel, PushNotificationChannel)

    def test_get_telegram_channel(self):
        """Test getting Telegram notification channel."""
        channel = get_notification_channel(NotificationType.TELEGRAM)
        assert isinstance(channel, TelegramNotificationChannel)

    def test_get_invalid_channel(self):
        """Test getting invalid notification channel raises error."""
        with pytest.raises(ValueError):
            get_notification_channel("invalid_type")


class TestEmailNotificationChannel:
    """Tests for EmailNotificationChannel."""

    @pytest.fixture
    def channel(self):
        """Create email channel instance."""
        return EmailNotificationChannel()

    @pytest.fixture
    def notification(self):
        """Create test notification."""
        return Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

    @pytest.fixture
    def user_settings(self):
        """Create user settings with email."""
        return UserNotificationsSettings(
            user_uuid=uuid4(),
            notification_channels={NotificationType.EMAIL: "test@example.com"},
            preferred_notification_channel=NotificationType.EMAIL,
        )

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.smtplib.SMTP"
    )
    def test_send_email_success(
        self,
        mock_smtp,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending email successfully."""
        mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_SERVER = "smtp.example.com"
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_PORT = 587
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_USERNAME = "user"
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_PASSWORD = "pass"
        mock_settings.EMAIL_NOTIFICATIONS_FROM_ADDRESS = "from@example.com"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        channel.send(notification)

        mock_provider.get_notification_settings.assert_called_once_with(
            notification.user_uuid
        )
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    def test_send_email_no_email_address(
        self, mock_get_user_provider, channel, notification
    ):
        """Test sending email when user has no email address."""
        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={},
            preferred_notification_channel=None,
        )

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        with pytest.raises(UserDoesntHaveTheChannel):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    def test_send_email_disabled(
        self,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending email when email notifications are disabled."""
        mock_settings.EMAIL_NOTIFICATIONS_ENABLED = False

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        channel.send(notification)  # Should return without error

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.smtplib.SMTP"
    )
    def test_send_email_smtp_error(
        self,
        mock_smtp,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending email with SMTP error."""
        mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_SERVER = "smtp.example.com"
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_PORT = 587
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_USERNAME = "user"
        mock_settings.EMAIL_NOTIFICATIONS_SMTP_PASSWORD = "pass"
        mock_settings.EMAIL_NOTIFICATIONS_FROM_ADDRESS = "from@example.com"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_server = MagicMock()
        mock_server.send_message.side_effect = smtplib.SMTPException(
            "SMTP Error"
        )
        mock_smtp.return_value.__enter__.return_value = mock_server

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)


class TestSMSNotificationChannel:
    """Tests for SMSNotificationChannel."""

    @pytest.fixture
    def channel(self):
        """Create SMS channel instance."""
        return SMSNotificationChannel()

    @pytest.fixture
    def notification(self):
        """Create test notification."""
        return Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.SMS,
            status=NotificationStatus.PENDING,
        )

    @pytest.fixture
    def user_settings(self):
        """Create user settings with SMS."""
        return UserNotificationsSettings(
            user_uuid=uuid4(),
            notification_channels={NotificationType.SMS: "+1234567890"},
            preferred_notification_channel=NotificationType.SMS,
        )

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_sms_success(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending SMS successfully."""
        mock_settings.SMS_NOTIFICATIONS_ENABLED = True
        mock_settings.SMS_NOTIFICATIONS_SERVICE_URL = (
            "https://api.sms.com/send"
        )
        mock_settings.SMS_NOTIFICATIONS_API_KEY = "api-key"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        channel.send(notification)

        mock_provider.get_notification_settings.assert_called_once_with(
            notification.user_uuid
        )
        mock_post.assert_called_once()

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    def test_send_sms_no_phone_number(
        self, mock_get_user_provider, channel, notification
    ):
        """Test sending SMS when user has no phone number."""
        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={},
            preferred_notification_channel=None,
        )

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        with pytest.raises(UserDoesntHaveTheChannel):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_sms_request_error(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending SMS with request error."""
        mock_settings.SMS_NOTIFICATIONS_ENABLED = True
        mock_settings.SMS_NOTIFICATIONS_SERVICE_URL = (
            "https://api.sms.com/send"
        )
        mock_settings.SMS_NOTIFICATIONS_API_KEY = "api-key"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_post.side_effect = RequestException("Connection error")

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    def test_send_sms_mock_mode(
        self,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending SMS in mock mode (no service URL or API key)."""
        mock_settings.SMS_NOTIFICATIONS_ENABLED = True
        mock_settings.SMS_NOTIFICATIONS_SERVICE_URL = None
        mock_settings.SMS_NOTIFICATIONS_API_KEY = None

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        channel.send(notification)  # Should return without error (mock mode)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_sms_non_200_response(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending SMS with non-200 response."""
        mock_settings.SMS_NOTIFICATIONS_ENABLED = True
        mock_settings.SMS_NOTIFICATIONS_SERVICE_URL = (
            "https://api.sms.com/send"
        )
        mock_settings.SMS_NOTIFICATIONS_API_KEY = "api-key"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)


class TestPushNotificationChannel:
    """Tests for PushNotificationChannel."""

    @pytest.fixture
    def channel(self):
        """Create push channel instance."""
        return PushNotificationChannel()

    @pytest.fixture
    def notification(self):
        """Create test notification."""
        return Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.PUSH,
            status=NotificationStatus.PENDING,
        )

    @pytest.fixture
    def user_settings(self):
        """Create user settings with push token."""
        return UserNotificationsSettings(
            user_uuid=uuid4(),
            notification_channels={NotificationType.PUSH: "push-token-123"},
            preferred_notification_channel=NotificationType.PUSH,
        )

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    def test_send_push_no_token(
        self, mock_get_user_provider, channel, notification
    ):
        """Test sending push when user has no push token."""
        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={},
            preferred_notification_channel=None,
        )

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        with pytest.raises(UserDoesntHaveTheChannel):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_push_success(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending push notification successfully."""
        mock_settings.PUSH_NOTIFICATIONS_ENABLED = True
        mock_settings.PUSH_NOTIFICATIONS_SERVICE_URL = (
            "https://api.push.com/send"
        )
        mock_settings.PUSH_NOTIFICATIONS_API_KEY = "api-key"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        channel.send(notification)

        mock_provider.get_notification_settings.assert_called_once_with(
            notification.user_uuid
        )
        mock_post.assert_called_once()

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    def test_send_push_disabled(
        self,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending push when notifications are disabled."""
        mock_settings.PUSH_NOTIFICATIONS_ENABLED = False

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    def test_send_push_mock_mode(
        self,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending push in mock mode (no service URL or API key)."""
        mock_settings.PUSH_NOTIFICATIONS_ENABLED = True
        mock_settings.PUSH_NOTIFICATIONS_SERVICE_URL = None
        mock_settings.PUSH_NOTIFICATIONS_API_KEY = None

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_push_non_200_response(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending push with non-200 response."""
        mock_settings.PUSH_NOTIFICATIONS_ENABLED = True
        mock_settings.PUSH_NOTIFICATIONS_SERVICE_URL = (
            "https://api.push.com/send"
        )
        mock_settings.PUSH_NOTIFICATIONS_API_KEY = "api-key"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_push_request_exception(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending push with RequestException."""
        mock_settings.PUSH_NOTIFICATIONS_ENABLED = True
        mock_settings.PUSH_NOTIFICATIONS_SERVICE_URL = (
            "https://api.push.com/send"
        )
        mock_settings.PUSH_NOTIFICATIONS_API_KEY = "api-key"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_post.side_effect = RequestException("Connection error")

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)


class TestTelegramNotificationChannel:
    """Tests for TelegramNotificationChannel."""

    @pytest.fixture
    def channel(self):
        """Create Telegram channel instance."""
        return TelegramNotificationChannel()

    @pytest.fixture
    def notification(self):
        """Create test notification."""
        return Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.TELEGRAM,
            status=NotificationStatus.PENDING,
        )

    @pytest.fixture
    def user_settings(self):
        """Create user settings with Telegram chat ID."""
        return UserNotificationsSettings(
            user_uuid=uuid4(),
            notification_channels={NotificationType.TELEGRAM: "123456789"},
            preferred_notification_channel=NotificationType.TELEGRAM,
        )

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    def test_send_telegram_no_chat_id(
        self, mock_get_user_provider, channel, notification
    ):
        """Test sending Telegram message when user has no chat ID."""
        user_settings = UserNotificationsSettings(
            user_uuid=notification.user_uuid,
            notification_channels={},
            preferred_notification_channel=None,
        )

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        with pytest.raises(UserDoesntHaveTheChannel):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_telegram_success(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending Telegram message successfully."""
        mock_settings.TELEGRAM_NOTIFICATIONS_ENABLED = True
        mock_settings.TELEGRAM_NOTIFICATIONS_BOT_TOKEN = "bot-token"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response

        channel.send(notification)

        mock_provider.get_notification_settings.assert_called_once_with(
            notification.user_uuid
        )
        mock_post.assert_called_once()

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers.notification_channels.settings"
    )
    def test_send_telegram_disabled(
        self,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending Telegram when notifications are disabled."""
        mock_settings.TELEGRAM_NOTIFICATIONS_ENABLED = False

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        channel.send(notification)  # Should return without error

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers.notification_channels.settings"
    )
    def test_send_telegram_mock_mode(
        self,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending Telegram in mock mode (no bot token)."""
        mock_settings.TELEGRAM_NOTIFICATIONS_ENABLED = True
        mock_settings.TELEGRAM_NOTIFICATIONS_BOT_TOKEN = None

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers.notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_telegram_non_200_response(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending Telegram with non-200 response."""
        mock_settings.TELEGRAM_NOTIFICATIONS_ENABLED = True
        mock_settings.TELEGRAM_NOTIFICATIONS_BOT_TOKEN = "bot-token"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"ok": False}
        mock_post.return_value = mock_response

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers.notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_telegram_not_ok_response(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending Telegram with ok=False in response."""
        mock_settings.TELEGRAM_NOTIFICATIONS_ENABLED = True
        mock_settings.TELEGRAM_NOTIFICATIONS_BOT_TOKEN = "bot-token"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": False}
        mock_post.return_value = mock_response

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)

    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.get_user_provider"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.settings"
    )
    @patch(
        "notification_service.adapters.workers"
        ".notification_channels.requests.post"
    )
    def test_send_telegram_request_exception(
        self,
        mock_post,
        mock_settings,
        mock_get_user_provider,
        channel,
        notification,
        user_settings,
    ):
        """Test sending Telegram with RequestException."""
        mock_settings.TELEGRAM_NOTIFICATIONS_ENABLED = True
        mock_settings.TELEGRAM_NOTIFICATIONS_BOT_TOKEN = "bot-token"

        mock_provider = Mock()
        mock_provider.get_notification_settings.return_value = user_settings
        mock_get_user_provider.return_value = mock_provider

        mock_post.side_effect = RequestException("Connection error")

        with pytest.raises(CouldntSendNotification):
            channel.send(notification)
