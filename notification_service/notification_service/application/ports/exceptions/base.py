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