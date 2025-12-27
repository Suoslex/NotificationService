class NotificationServiceError(Exception):
    message: str = "There was an error in the notification service workflow."

    def __init__(self, message: str = None, *args):
        super().__init__(message or self.message, *args)


class TemporaryFailure(NotificationServiceError):
    message: str = "Temporary failure in executing."


class UserProviderError(Exception):
    message: str = "There was an error with UserProvider."


class UserNotFound(UserProviderError):
    message: str = "Requested user is not found."


class RepositoryError(NotificationServiceError):
    message: str = "There was an error with repository."


class ObjectNotFoundInRepository(RepositoryError):
    message: str = "Object was not found in the repository."
