import os
import smtplib
from abc import ABC, abstractmethod
from dataclasses import asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from django.conf import settings
from loguru import logger

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
        try:
            user_settings = user_provider.get_notification_settings(notification.user_id)
            email_address = user_settings.notification_channels.get(NotificationType.EMAIL)
            
            if not email_address:
                logger.error(f"No email address found for user {notification.user_id}")
                raise ValueError(f"No email address found for user {notification.user_id}")
            
            if not settings.EMAIL_NOTIFICATIONS_ENABLED:
                logger.info(f"Email notifications disabled, skipping for user {notification.user_id}")
                return
            
            msg = MIMEMultipart()
            msg['From'] = "notification@photopoint.com"
            msg['To'] = email_address
            msg['Subject'] = notification.title or "Notification"
            
            body = notification.content
            msg.attach(MIMEText(body, 'plain'))
            
            smtp_server = settings.EMAIL_NOTIFICATIONS_SMTP_SERVER
            smtp_port = settings.EMAIL_NOTIFICATIONS_SMTP_PORT
            smtp_username = settings.EMAIL_NOTIFICATIONS_SMTP_USERNAME
            smtp_password = settings.EMAIL_NOTIFICATIONS_SMTP_PASSWORD
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            
            text = msg.as_string()
            server.sendmail(msg['From'], email_address, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {email_address} for notification {notification.uuid}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise


class SMSNotificationChannel(NotificationChannel):
    """
    SMS notification channel.

    Sends notifications via SMS.
    """
    type = NotificationType.SMS
    def send(self, notification: Notification):
        user_provider = get_user_provider()
        try:
            user_settings = user_provider.get_notification_settings(notification.user_id)
            sms_number = user_settings.notification_channels.get(NotificationType.SMS)
            
            if not sms_number:
                logger.error(f"No SMS number found for user {notification.user_id}")
                raise ValueError(f"No SMS number found for user {notification.user_id}")
            
            if not settings.SMS_NOTIFICATIONS_ENABLED:
                logger.info(f"SMS notifications disabled, skipping for user {notification.user_id}")
                return

            sms_service_url = settings.SMS_NOTIFICATIONS_SERVICE_URL
            sms_api_key = settings.SMS_NOTIFICATIONS_API_KEY
            
            if sms_service_url and sms_api_key:
                payload = {
                    "to": sms_number,
                    "message": notification.content,
                    "sender": "PhotoPoint"
                }
                headers = {
                    "Authorization": f"Bearer {sms_api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.post(sms_service_url, json=payload, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"SMS sending failed with status {response.status_code}")
                    raise Exception(f"SMS sending failed with status {response.status_code}")
            else:
                logger.info(f"Mock SMS sent to {sms_number}: {notification.content}")
            
            logger.info(f"SMS sent successfully to {sms_number} for notification {notification.uuid}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            raise


class PushNotificationChannel(NotificationChannel):
    """
    Push notification channel.

    Sends notifications via push notifications.
    """
    type = NotificationType.PUSH
    def send(self, notification: Notification):
        user_provider = get_user_provider()
        try:
            user_settings = user_provider.get_notification_settings(notification.user_id)
            push_token = user_settings.notification_channels.get(NotificationType.PUSH)
            
            if not push_token:
                logger.error(f"No push token found for user {notification.user_id}")
                raise ValueError(f"No push token found for user {notification.user_id}")
            
            if not settings.PUSH_NOTIFICATIONS_ENABLED:
                logger.info(f"Push notifications disabled, skipping for user {notification.user_id}")
                return

            push_service_url = settings.PUSH_NOTIFICATIONS_SERVICE_URL
            push_api_key = settings.PUSH_NOTIFICATIONS_API_KEY
            
            if push_service_url and push_api_key:
                payload = {
                    "tokens": [push_token],
                    "notification": {
                        "title": notification.title or "Notification",
                        "body": notification.content
                    },
                    "data": {
                        "notification_uuid": str(notification.uuid)
                    }
                }
                headers = {
                    "Authorization": f"Bearer {push_api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.post(push_service_url, json=payload, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"Push notification sending failed with status {response.status_code}")
                    raise Exception(f"Push notification sending failed with status {response.status_code}")
            else:
                logger.info(f"Mock push notification sent to token {push_token}: {notification.title} - {notification.content}")
            
            logger.info(f"Push notification sent successfully to {push_token} for notification {notification.uuid}")
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            raise


class TelegramNotificationChannel(NotificationChannel):
    """
    Telegram notification channel.

    Sends notifications via Telegram.
    """
    type = NotificationType.TELEGRAM
    def send(self, notification: Notification):
        user_provider = get_user_provider()
        try:
            user_settings = user_provider.get_notification_settings(notification.user_id)
            telegram_chat_id = user_settings.notification_channels.get(NotificationType.TELEGRAM)
            
            if not telegram_chat_id:
                logger.error(f"No Telegram chat ID found for user {notification.user_id}")
                raise ValueError(f"No Telegram chat ID found for user {notification.user_id}")
            
            if not settings.TELEGRAM_NOTIFICATIONS_ENABLED:
                logger.info(f"Telegram notifications disabled, skipping for user {notification.user_id}")
                return
            
            telegram_bot_token = settings.TELEGRAM_NOTIFICATIONS_BOT_TOKEN
            
            if telegram_bot_token:
                telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                payload = {
                    "chat_id": telegram_chat_id,
                    "text": f"{notification.title or 'Notification'}\n\n{notification.content}",
                    "parse_mode": "HTML"
                }
                response = requests.post(telegram_api_url, data=payload)
                
                if response.status_code != 200 or not response.json().get("ok"):
                    logger.error(f"Telegram message sending failed with status {response.status_code}")
                    raise Exception(f"Telegram message sending failed with status {response.status_code}")
            else:
                logger.info(f"Mock Telegram message sent to chat {telegram_chat_id}: {notification.title} - {notification.content}")
            
            logger.info(f"Telegram message sent successfully to {telegram_chat_id} for notification {notification.uuid}")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            raise