from notification_service.application.dtos import NotificationStatusDTO
from notification_service.domain.entities import Notification
from notification_service.application.ports.unit_of_work import (
    UnitOfWorkPort
)

class SendNotificationUseCase:
    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    def execute(self, notification: Notification) -> NotificationStatusDTO:
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
