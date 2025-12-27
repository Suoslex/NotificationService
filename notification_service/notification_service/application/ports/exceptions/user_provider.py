from notification_service.application.ports.exceptions.base import (
    NotificationServiceError
)


class UserProviderError(NotificationServiceError):
    """
    Base exception class for errors occurring in the user provider.
    """
    message: str = "There was an error with UserProvider."


class UserNotFound(UserProviderError):
    """
    Raised when the requested user cannot be found in the user provider.
    """
    message: str = "Requested user is not found."