from datetime import datetime
from uuid import UUID

from django.db import models

from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus
)


_NotificationChoices = models.TextChoices(
    '_NotificationChoices',
    [(val.name, val.value) for val in NotificationType]
)

_NotificationStatusChoices = models.TextChoices(
    '_NotificationStatusChoices',
    [(val.name, val.value) for val in NotificationStatus]
)

class NotificationModel(models.Model):
    # TODO: Indexes

    uuid: UUID = models.UUIDField()
    user_id: int = models.IntegerField()
    title: str = models.CharField()
    text: str = models.CharField()
    type: NotificationType | None = models.CharField(
        null=True,
        choices=_NotificationChoices.choices,
        default=None
    )
    status: NotificationStatus = models.CharField(
        choices=_NotificationStatusChoices.choices,
        default=_NotificationStatusChoices.PENDING
    )
    sent_at: datetime = models.DateTimeField(null=True, default=None)



