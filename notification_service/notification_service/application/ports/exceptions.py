class NotificationServiceError(Exception):
    """
    Base exception class for errors occurring in the notification service workflow.
    """
    message: str = "There was an error in the notification service workflow."

    def __init__(self, message: str = None, *args) -> None:
        """
        Initialize the exception with a custom message.

        Parameters
        ----------
        message : str | None
            Custom error message. If not provided, self.message is used.
        *args
            Additional arguments
        """
        super().__init__(message or self.message, *args)


class TemporaryFailure(NotificationServiceError):
    """
    Exception for temporary failures in execution.
    Raised when there is a temporary failure during execution 
    that might be resolved by retrying.
    """
    message: str = "Temporary failure in executing."


class UserProviderError(Exception):
    """
    Base exception class for errors occurring in the user provider.
    """
    message: str = "There was an error with UserProvider."


class UserNotFound(UserProviderError):
    """
    Raised when the requested user cannot be found in the user provider.
    """
    message: str = "Requested user is not found."


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
