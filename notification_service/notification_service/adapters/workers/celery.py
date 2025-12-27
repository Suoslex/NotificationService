from celery import shared_task
from loguru import logger

from notification_service.adapters.dependencies import (
    get_unit_of_work,
    get_user_provider
)
from notification_service.application.ports.exceptions import (
    UserNotFound,
)
from notification_service.domain.enums import NotificationStatus
from notification_service.adapters.workers.notification_channels import (
    get_notification_channel
)


@shared_task(autoretry_for=(Exception,), retry_backoff=5)
def send_notifications():
    logger.info("Checking for pending notifications to send")
    uow = get_unit_of_work()
    user_provider = get_user_provider()

    with uow:
        notification = uow.notification_repo.get_pending_for_update()
        logger.debug(f"Fetched notification: {notification}")
        if not notification:
            logger.info("No notification is pending right now.")
            return
        try:
            user_settings = user_provider.get_notification_settings(
                user_id=notification.user_id
            )
        except UserNotFound:
            notification.status = NotificationStatus.FAILED
            uow.notification_repo.update(notification)
            return
        if notification.type:
            if notification.type not in user_settings.notification_channels:
                notification.status = NotificationStatus.FAILED
                uow.notification_repo.update(notification)
                return
            notification_channel_types = [notification.type]
        else:
            notification_channel_types = [
                user_settings.preferred_notification_channel,
                *(
                    set(user_settings.notification_channels)
                    - {user_settings.preferred_notification_channel}
                )
            ]
        for channel_type in notification_channel_types:
            for _ in range(3):
                try:
                    channel = get_notification_channel(channel_type)
                    channel.send(notification)
                except Exception as error:
                    continue
                break
            else:
                continue
            notification.status = NotificationStatus.SENT
            uow.notification_repo.update(notification)
            return
        notification.status = NotificationStatus.FAILED
        uow.notification_repo.update(notification)
        return
