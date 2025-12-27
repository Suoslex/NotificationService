from notification_service.application.dtos.notification_status import (
    NotificationStatusDTO
)
from notification_service.domain.entities import Notification
from notification_service.application.ports.unit_of_work import (
    UnitOfWorkPort
)

class SendNotificationUseCase:
    """
    Use case for sending notifications.
    Handles the logic for creating and processing notifications.
    """
    def __init__(self, uow: UnitOfWorkPort) -> None:
        """
        Initialize the use case with a unit of work.

        Parameters
        ----------
        uow : UnitOfWorkPort
            Unit of work instance
        """
        self.uow = uow

    def execute(self, notification: Notification) -> NotificationStatusDTO:
        """
        Execute the use case to send a notification.

        Parameters
        ----------
        notification : Notification
            Notification object to send

        Returns
        ----------
        NotificationStatusDTO
            Status information of the notification
        """
        was_created = False
        if self.uow.notification_repo.exists(notification.uuid):
            notification = self.uow.notification_repo.get_by_uuid(
                notification.uuid
            )
        else:
            with self.uow:
                notification = self.uow.notification_repo.create(notification)
            was_created = True
        return NotificationStatusDTO(
            uuid=notification.uuid,
            status=notification.status,
            was_created=was_created
        )
