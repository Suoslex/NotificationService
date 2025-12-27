from notification_service.application.ports.exceptions.base import (
    NotificationServiceError
)


class RepositoryError(NotificationServiceError):
    """
    Base exception class for errors occurring in the repository layer.
    """
    message: str = "There was an error with repository."


class ObjectNotFoundInRepository(RepositoryError):
    """
    Raised when the requested object cannot be found in the repository.
    """
    message: str = "Object was not found in the repository."
