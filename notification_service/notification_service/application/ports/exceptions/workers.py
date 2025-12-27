from notification_service.application.ports.exceptions.base import (
    NotificationServiceError
)


class NotificationWorkerError(NotificationServiceError):
    message: str = "There was an error with Notification worker."


class NotificationChannelError(NotificationWorkerError):
    message: str = "There was an error with notification channel."


class UserDoesntHaveTheChannel(NotificationChannelError):
    message: str = (
        "User doesn't have suitable notification channel configuration."
    )


class CouldntSendNotification(NotificationChannelError):
    message: str = "Couldn't send notification."