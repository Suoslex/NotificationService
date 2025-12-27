from abc import ABC, abstractmethod
from dataclasses import asdict

from notification_service.domain.entities import Notification
from notification_service.domain.enums import NotificationType


def get_notification_channel(
        notification_type: NotificationType
) -> "NotificationChannel":
    """
    Get notification channel instance based on notification type.

    Parameters
    ----------
    notification_type : NotificationType
        Type of notification channel to get

    Returns
    ----------
    NotificationChannel
        Instance of the requested notification channel

    Raises
    ----------
    ValueError
        If notification type is not supported
    """
    channels = {
        NotificationType.EMAIL: EmailNotificationChannel(),
        NotificationType.SMS: SMSNotificationChannel(),
        NotificationType.PUSH: PushNotificationChannel(),
        NotificationType.TELEGRAM: TelegramNotificationChannel()
    }
    if notification_type not in channels:
        raise ValueError(
            f"Notification type {notification_type} is not supported "
            f"by any notification channel."
        )
    return channels[notification_type]


class NotificationChannel(ABC):
    """
    Abstract base class for notification channels.

    Defines the interface for different types of notification channels.
    """
    type: NotificationType

    @abstractmethod
    def send(self, notification: Notification):
        """
        Send notification through the channel.

        Parameters
        ----------
        notification : Notification
            Notification object to send

        Raises
        ----------
        NotImplementedError
            Method is not implemented
        """
        ...



class EmailNotificationChannel(NotificationChannel):
    """
    Email notification channel.

    Sends notifications via email.
    """
    def send(self, notification: Notification):
        print(f"Email sent: {asdict(notification)}")


class SMSNotificationChannel(NotificationChannel):
    """
    SMS notification channel.

    Sends notifications via SMS.
    """
    def send(self, notification: Notification):
        print(f"SMS sent: {asdict(notification)}")


class PushNotificationChannel(NotificationChannel):
    """
    Push notification channel.

    Sends notifications via push notifications.
    """
    def send(self, notification: Notification):
        print(f"Push sent: {asdict(notification)}")


class TelegramNotificationChannel(NotificationChannel):
    """
    Telegram notification channel.

    Sends notifications via Telegram.
    """
    def send(self, notification: Notification):
        print(f"Telegram message sent: {asdict(notification)}")