from abc import ABC, abstractmethod

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
        pass


class SMSNotificationChannel(NotificationChannel):
    def send(self, notification: Notification):
        pass


class PushNotificationChannel(NotificationChannel):
    def send(self, notification: Notification):
        pass


class TelegramNotificationChannel(NotificationChannel):
    def send(self, notification: Notification):
        pass