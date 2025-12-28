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
    logger.debug(f"Getting notification channel for type: {notification_type}")
    channels = {
        NotificationType.EMAIL: EmailNotificationChannel(),
        NotificationType.SMS: SMSNotificationChannel(),
        NotificationType.PUSH: PushNotificationChannel(),
        NotificationType.TELEGRAM: TelegramNotificationChannel()
    }
    if notification_type not in channels:
        message = (
            f"Notification type {notification_type} is not supported "
            f"by any notification channel."
        )
        logger.error(message)
        raise ValueError(message)
    logger.debug(f"Successfully retrieved channel for type: {notification_type}")
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
        logger.debug(
            f"Sending email notification {notification.uuid} "
            f"to user {notification.user_uuid}"
        )
        user_provider = get_user_provider()
        logger.debug(
            f"Fetching user settings for user {notification.user_uuid}"
        )
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        logger.debug(
            f"Retrieved user settings: {user_settings.notification_channels}"
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
        
        logger.debug(
            f"Found email address {email_address} "
            f"for user {notification.user_uuid}"
        )

        if not settings.EMAIL_NOTIFICATIONS_ENABLED:
            logger.info(
                f"Email notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return

        try:
            logger.debug(
                f"Attempting to send email to {email_address} "
                f"for notification {notification.uuid}"
            )
            self._send_email(
                to_email=email_address,
                subject=notification.title or "Notification",
                body=notification.text,
                from_email=settings.EMAIL_NOTIFICATIONS_FROM_ADDRESS
            )
            logger.debug(
                f"Email sent successfully to {email_address} for notification "
                f"{notification.uuid}"
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
        logger.debug(
            f"Sending SMS notification {notification.uuid} "
            f"to user {notification.user_uuid}"
        )
        user_provider = get_user_provider()
        logger.debug(
            f"Fetching user settings for user {notification.user_uuid}"
        )
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        logger.debug(
            f"Retrieved user settings: {user_settings.notification_channels}"
        )
        sms_number = user_settings.notification_channels.get(
            NotificationType.SMS
        )

        if not sms_number:
            message = f"No SMS number found for user {notification.user_uuid}"
            logger.error(message)
            raise UserDoesntHaveTheChannel(message)
        
        logger.debug(
            f"Found SMS number {sms_number} for user {notification.user_uuid}"
        )

        if not settings.SMS_NOTIFICATIONS_ENABLED:
            logger.info(
                f"SMS notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return
        try:
            logger.debug(
                f"Attempting to send SMS to {sms_number} for notification "
                f"{notification.uuid}"
            )
            self._send_sms(
                to_number=sms_number,
                message=notification.text
            )
            logger.debug(
                f"SMS sent successfully to {sms_number} for notification "
                f"{notification.uuid}"
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
        logger.debug(
            f"Sending push notification {notification.uuid} "
            f"to user {notification.user_uuid}"
        )
        user_provider = get_user_provider()
        logger.debug(
            f"Fetching user settings for user {notification.user_uuid}"
        )
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        logger.debug(
            f"Retrieved user settings: {user_settings.notification_channels}"
        )
        push_token = user_settings.notification_channels.get(
            NotificationType.PUSH
        )
            
        if not push_token:
            message = f"No push token found for user {notification.user_uuid}"
            logger.error(message)
            raise UserDoesntHaveTheChannel(message)
        
        logger.debug(
            f"Found push token {push_token} for user {notification.user_uuid}"
        )

        if not settings.PUSH_NOTIFICATIONS_ENABLED:
            logger.info(
                f"Push notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return

        try:
            logger.debug(
                f"Attempting to send push notification to {push_token} for "
                f"notification {notification.uuid}"
            )
            self._send_push(
                push_token=push_token,
                title=notification.title,
                body=notification.text,
                notification_uuid=notification.uuid,
            )
            logger.debug(
                f"Push notification sent successfully to {push_token} for "
                f"notification {notification.uuid}"
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
        logger.debug(
            f"Sending Telegram notification {notification.uuid} "
            f"to user {notification.user_uuid}"
        )
        user_provider = get_user_provider()
        logger.debug(
            f"Fetching user settings for user {notification.user_uuid}"
        )
        user_settings = user_provider.get_notification_settings(
            notification.user_uuid
        )
        logger.debug(
            f"Retrieved user settings: {user_settings.notification_channels}"
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
        
        logger.debug(
            f"Found Telegram chat ID {telegram_chat_id} for user "
            f"{notification.user_uuid}"
        )

        if not settings.TELEGRAM_NOTIFICATIONS_ENABLED:
            logger.info(
                f"Telegram notifications disabled, "
                f"skipping for user {notification.user_uuid}"
            )
            return

        try:
            logger.debug(
                f"Attempting to send Telegram message to {telegram_chat_id} "
                f"for notification {notification.uuid}"
            )
            self._send_message_in_telegram(
                chat_id=telegram_chat_id,
                title=notification.title,
                body=notification.text,
            )
            logger.debug(
                f"Telegram message sent successfully to {telegram_chat_id} "
                f"for notification {notification.uuid}"
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
    