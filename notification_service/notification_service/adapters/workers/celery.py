from celery import shared_task
from loguru import logger

from notification_service.adapters.dependencies import (
    get_unit_of_work,
    get_user_provider
)
from notification_service.application.ports.exceptions.base import (
    NotificationServiceError
)
from notification_service.application.ports.exceptions.workers import (
    NotificationChannelError
)
from notification_service.application.ports.exceptions.user_provider import (
    UserNotFound,
)
from notification_service.domain.enums import NotificationStatus
from notification_service.adapters.workers.notification_channels import (
    get_notification_channel
)


@shared_task(
    autoretry_for=(NotificationServiceError,),
    retry_backoff_max=500,
    retry_backoff=5,
    max_retries=5
)
def send_notifications():
    """
    Celery task to send pending notifications.

    Fetches pending notifications from the database and sends them
    using appropriate notification channels based on user preferences.
    """
    logger.info("Checking for pending notifications to send")
    uow = get_unit_of_work()
    user_provider = get_user_provider()

    with uow:
        notification = uow.notification_repo.get_pending_for_update()
        logger.debug(f"Fetched notification: {notification}")
        if not notification:
            logger.debug("No notification is pending right now.")
            return
        
        logger.info(
            f"Processing notification {notification.uuid} for "
            f"user {notification.user_uuid}"
        )
        
        try:
            user_settings = user_provider.get_notification_settings(
                user_uuid=notification.user_uuid
            )
            logger.debug(
                f"Retrieved user settings for "
                f"{notification.user_uuid}: {user_settings}"
            )
        except UserNotFound:
            logger.warning(
                f"User {notification.user_uuid} not found, "
                f"marking notification {notification.uuid} "
                f"as FAILED"
            )
            notification.status = NotificationStatus.FAILED
            uow.notification_repo.update(notification)
            return
        
        if notification.type:
            logger.debug(
                f"Notification has specific type: "
                f"{notification.type}"
            )
            if notification.type not in user_settings.notification_channels:
                logger.warning(
                    f"User {notification.user_uuid} does not "
                    f"have {notification.type} enabled, marking "
                    f"notification {notification.uuid} as FAILED"
                )
                notification.status = NotificationStatus.FAILED
                uow.notification_repo.update(notification)
                return
            notification_channel_types = [notification.type]
        else:
            logger.debug(
                f"Notification has no specific type, using "
                f"user preferences"
            )
            notification_channel_types = [
                *(
                    set(user_settings.notification_channels)
                    - {user_settings.preferred_notification_channel}
                )
            ]
            if user_settings.preferred_notification_channel:
                notification_channel_types.insert(
                    0,
                    user_settings.preferred_notification_channel
                )
        
        logger.debug(
            f"Attempting to send notification via channels: "
            f"{notification_channel_types}"
        )
        
        for channel_type in notification_channel_types:
            logger.info(
                f"Attempting to send notification "
                f"{notification.uuid} via {channel_type} channel"
            )
            for attempt in range(3):
                try:
                    logger.debug(
                        f"Attempt {attempt + 1} to send via "
                        f"{channel_type}"
                    )
                    channel = get_notification_channel(channel_type)
                    logger.debug(
                        f"Successfully got channel for {channel_type}"
                    )
                    channel.send(notification)
                    break
                except NotificationChannelError as error:
                    logger.warning(
                        f"Failed to send notification "
                        f"{notification.uuid} via {channel_type} "
                        f"on attempt {attempt + 1}: {str(error)}"
                    )
                    continue
                except Exception as e:
                    logger.error(
                        f"Unexpected error sending notification "
                        f"{notification.uuid} via {channel_type}: "
                        f"{str(e)}"
                    )
                    continue
            else:
                logger.info(
                    f"All 3 attempts failed for channel {channel_type}, "
                    f"trying next channel"
                )
                continue
            logger.info(
                f"Successfully sent notification "
                f"{notification.uuid} via {channel_type} "
                f"on attempt {attempt + 1}"
            )
            notification.status = NotificationStatus.SENT
            uow.notification_repo.update(notification)
            return
        logger.warning(
            f"All notification channels failed for notification "
            f"{notification.uuid}, marking as FAILED"
        )
        notification.status = NotificationStatus.FAILED
        uow.notification_repo.update(notification)
        return