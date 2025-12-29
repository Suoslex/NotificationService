"""Tests for application exceptions."""

from notification_service.application.ports.exceptions.base import (
    NotificationServiceError,
    TemporaryFailure,
)
from notification_service.application.ports.exceptions.repository import (
    RepositoryError,
    ObjectNotFoundInRepository,
)
from notification_service.application.ports.exceptions.user_provider import (
    UserProviderError,
    UserNotFound,
)
from notification_service.application.ports.exceptions.workers import (
    NotificationWorkerError,
    NotificationChannelError,
    UserDoesntHaveTheChannel,
    CouldntSendNotification,
)


class TestNotificationServiceError:
    """Tests for base NotificationServiceError."""

    def test_default_message(self):
        """Test exception with default message."""
        error = NotificationServiceError()
        assert (
            str(error)
            == "There was an error in the notification service workflow."
        )

    def test_custom_message(self):
        """Test exception with custom message."""
        custom_msg = "Custom error message"
        error = NotificationServiceError(custom_msg)
        assert str(error) == custom_msg


class TestTemporaryFailure:
    """Tests for TemporaryFailure exception."""

    def test_temporary_failure_message(self):
        """Test TemporaryFailure default message."""
        error = TemporaryFailure()
        assert str(error) == "Temporary failure in executing."


class TestRepositoryError:
    """Tests for repository exceptions."""

    def test_repository_error_inheritance(self):
        """Test that RepositoryError inherits from NotificationServiceError."""
        error = RepositoryError()
        assert isinstance(error, NotificationServiceError)

    def test_object_not_found_inheritance(self):
        """
        Test that ObjectNotFoundInRepository inherits from RepositoryError.
        """
        error = ObjectNotFoundInRepository()
        assert isinstance(error, RepositoryError)
        assert isinstance(error, NotificationServiceError)

    def test_object_not_found_message(self):
        """Test ObjectNotFoundInRepository message."""
        error = ObjectNotFoundInRepository()
        assert "not found" in str(error).lower()


class TestUserProviderError:
    """Tests for user provider exceptions."""

    def test_user_provider_error_inheritance(self):
        """T
        est that UserProviderError inherits from NotificationServiceError.
        """
        error = UserProviderError()
        assert isinstance(error, NotificationServiceError)

    def test_user_not_found_inheritance(self):
        """Test that UserNotFound inherits from UserProviderError."""
        error = UserNotFound()
        assert isinstance(error, UserProviderError)
        assert isinstance(error, NotificationServiceError)

    def test_user_not_found_message(self):
        """Test UserNotFound message."""
        error = UserNotFound()
        assert "not found" in str(error).lower()


class TestNotificationWorkerError:
    """Tests for worker exceptions."""

    def test_notification_worker_error_inheritance(self):
        """
        Test that NotificationWorkerError inherits
        from NotificationServiceError.
        """
        error = NotificationWorkerError()
        assert isinstance(error, NotificationServiceError)

    def test_notification_channel_error_inheritance(self):
        """
        Test that NotificationChannelError inherits
        from NotificationWorkerError.
        """
        error = NotificationChannelError()
        assert isinstance(error, NotificationWorkerError)
        assert isinstance(error, NotificationServiceError)

    def test_user_doesnt_have_channel_inheritance(self):
        """
        Test that UserDoesntHaveTheChannel inherits
        from NotificationChannelError.
        """
        error = UserDoesntHaveTheChannel()
        assert isinstance(error, NotificationChannelError)
        assert isinstance(error, NotificationWorkerError)
        assert isinstance(error, NotificationServiceError)

    def test_couldnt_send_notification_inheritance(self):
        """
        Test that CouldntSendNotification inherits
        from NotificationChannelError.
        """
        error = CouldntSendNotification()
        assert isinstance(error, NotificationChannelError)
        assert isinstance(error, NotificationWorkerError)
        assert isinstance(error, NotificationServiceError)

    def test_custom_messages(self):
        """Test custom messages for worker exceptions."""
        custom_msg = "Custom worker error"
        error = NotificationWorkerError(custom_msg)
        assert str(error) == custom_msg
