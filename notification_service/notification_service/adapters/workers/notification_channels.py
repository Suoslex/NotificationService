from abc import ABC, abstractmethod
from dataclasses import asdict

from notification_service.domain.entities import Notification
from notification_service.domain.enums import NotificationType


def get_notification_channel(
        notification_type: NotificationType
) -> "NotificationChannel":
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
    type: NotificationType

    @abstractmethod
    def send(self, notification: Notification): ...



class EmailNotificationChannel(NotificationChannel):
    def send(self, notification: Notification):
        print(f"Email sent: {asdict(notification)}")


class SMSNotificationChannel(NotificationChannel):
    def send(self, notification: Notification):
        print(f"SMS sent: {asdict(notification)}")


class PushNotificationChannel(NotificationChannel):
    def send(self, notification: Notification):
        print(f"Push sent: {asdict(notification)}")


class TelegramNotificationChannel(NotificationChannel):
    def send(self, notification: Notification):
        print(f"Telegram message sent: {asdict(notification)}")