import smtplib
from uuid import UUID
from abc import ABC, abstractmethod
from email.message import EmailMessage

import requests
from requests.exceptions import RequestException
from django.conf import settings
from loguru import logger

from notification_service.application.ports.exceptions.workers import (
    CouldntSendNotification,
    UserDoesntHaveTheChannel
)
from notification_service.domain.entities import Notification
from notification_service.domain.enums import NotificationType
from notification_service.adapters.dependencies import get_user_provider


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
        """
        ...



class EmailNotificationChannel(NotificationChannel):
    """
    Email notification channel.

    Sends notifications via email.
    """
    type = NotificationType.EMAIL
    
    def send(self, notification: Notification):
        user_provider = get_user_provider()
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        email_address = user_settings.notification_channels.get(
            NotificationType.EMAIL
        )

        if not email_address:
            message = (
                f"No email address found for user {notification.user_uuid}"
            )
            logger.error(message)
            raise UserDoesntHaveTheChannel(message)

        if not settings.EMAIL_NOTIFICATIONS_ENABLED:
            logger.info(
                f"Email notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return

        try:
            self._send_email(
                to_email=email_address,
                subject=notification.title or "Notification",
                body=notification.text,
                from_email=settings.EMAIL_NOTIFICATIONS_FROM_ADDRESS
            )
        except smtplib.SMTPException as e:
            message = f"SMTP error: {str(e)}"
            logger.error(message)
            raise CouldntSendNotification(message)
            
        logger.info(
            f"Email sent successfully to {email_address} "
            f"for notification {notification.uuid}"
        )

    def _send_email(
            self,
            to_email: str,
            subject: str,
            body: str,
            from_email: str
    ):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(body)

        smtp_server = settings.EMAIL_NOTIFICATIONS_SMTP_SERVER
        smtp_port = settings.EMAIL_NOTIFICATIONS_SMTP_PORT
        smtp_username = settings.EMAIL_NOTIFICATIONS_SMTP_USERNAME
        smtp_password = settings.EMAIL_NOTIFICATIONS_SMTP_PASSWORD

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)


class SMSNotificationChannel(NotificationChannel):
    """
    SMS notification channel.

    Sends notifications via SMS.
    """
    type = NotificationType.SMS
    
    def send(self, notification: Notification):
        user_provider = get_user_provider()
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        sms_number = user_settings.notification_channels.get(
            NotificationType.SMS
        )

        if not sms_number:
            message = f"No SMS number found for user {notification.user_uuid}"
            logger.error(message)
            raise UserDoesntHaveTheChannel(message)

        if not settings.SMS_NOTIFICATIONS_ENABLED:
            logger.info(
                f"SMS notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return
        try:
            self._send_sms(
                to_number=sms_number,
                message=notification.text
            )
        except RequestException as e:
            message = f"Failed to send SMS: {str(e)}"
            logger.error(message)
            raise CouldntSendNotification(message)

        logger.info(
            f"SMS sent successfully to {sms_number} "
            f"for notification {notification.uuid}"
        )
    
    def _send_sms(self, to_number: str, message: str):
        service_url = settings.SMS_NOTIFICATIONS_SERVICE_URL
        api_key = settings.SMS_NOTIFICATIONS_API_KEY

        if not service_url or not api_key:
            logger.info(f"Mock SMS sent to {to_number}: {message}")
            return

        payload = {
            "to": to_number,
            "message": message,
            "sender": "PhotoPoint"
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            service_url,
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            message = f"SMS sending failed with status {response.status_code}"
            logger.error(message)
            raise RequestException(message)



class PushNotificationChannel(NotificationChannel):
    """
    Push notification channel.

    Sends notifications via push notifications.
    """
    type = NotificationType.PUSH
    
    def send(self, notification: Notification):
        user_provider = get_user_provider()
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        push_token = user_settings.notification_channels.get(
            NotificationType.PUSH
        )
            
        if not push_token:
            logger.error(
                f"No push token found for user {notification.user_uuid}"
            )
            raise UserDoesntHaveTheChannel(
                f"No push token found for user {notification.user_uuid}"
            )

        if not settings.PUSH_NOTIFICATIONS_ENABLED:
            logger.info(
                f"Push notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return

        try:
            self._send_push(
                push_token=push_token,
                title=notification.title,
                body=notification.text,
                notification_uuid=notification.uuid,
            )
            
            logger.info(
                f"Push notification sent successfully to {push_token} "
                f"for notification {notification.uuid}"
            )
        except RequestException as e:
            message = f"Failed to send push notification: {str(e)}"
            logger.error(message)
            raise CouldntSendNotification(message)

    def _send_push(
            self,
            push_token: str,
            title: str,
            body: str,
            notification_uuid: UUID
    ):
        service_url = settings.PUSH_NOTIFICATIONS_SERVICE_URL
        api_key = settings.PUSH_NOTIFICATIONS_API_KEY
        if not service_url or not api_key:
            logger.info(
                f"Mock push notification sent to token "
                f"{push_token}: {title} - {body}"
            )
            return
        payload = {
            "tokens": [push_token],
            "notification": {
                "title": title or "Notification",
                "body": body
            },
            "data": {
                "notification_uuid": str(notification_uuid)
            }
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            service_url,
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            logger.error(
                f"Push notification sending failed with status "
                f"{response.status_code}"
            )
            raise RequestException(
                f"Push notification sending failed "
                f"with status {response.status_code}"
            )


class TelegramNotificationChannel(NotificationChannel):
    """
    Telegram notification channel.

    Sends notifications via Telegram.
    """
    type = NotificationType.TELEGRAM

    def send(self, notification: Notification):
        user_provider = get_user_provider()
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        telegram_chat_id = user_settings.notification_channels.get(
            NotificationType.TELEGRAM
        )

        if not telegram_chat_id:
            message = (
                f"No Telegram chat ID found for user "
                f"{notification.user_uuid}"
            )
            logger.error(message)
            raise UserDoesntHaveTheChannel(message)

        if not settings.TELEGRAM_NOTIFICATIONS_ENABLED:
            logger.info(
                f"Telegram notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return

        try:
            self._send_message_in_telegram(
                chat_id=telegram_chat_id,
                title=notification.title,
                body=notification.text,
            )
        except RequestException as e:
            message = f"Failed to send Telegram message: {str(e)}"
            logger.error(message)
            raise CouldntSendNotification(message)
        logger.info(
            f"Telegram message sent successfully to "
            f"{telegram_chat_id} for notification {notification.uuid}"
        )

    def _send_message_in_telegram(self, chat_id: str, title: str, body: str):
        bot_token = settings.TELEGRAM_NOTIFICATIONS_BOT_TOKEN
        if not bot_token:
            logger.info(
                f"Mock Telegram message sent to chat "
                f"{chat_id}: {title} - {body}"
            )
            return
        telegram_api_url = (
            f"https://api.telegram.org/bot{bot_token}/sendMessage"
        )
        payload = {
            "chat_id": chat_id,
            "text": f"{title or 'Notification'}\n\n{body}",
            "parse_mode": "HTML"
        }
        response = requests.post(telegram_api_url, data=payload)

        if response.status_code != 200 or not response.json().get("ok"):
            logger.error(
                f"Telegram message sending failed "
                f"with status {response.status_code}"
            )
            raise RequestException(
                f"Telegram message sending failed "
                f"with status {response.status_code}"
            )
    