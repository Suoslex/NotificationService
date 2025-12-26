from abc import ABC, abstractmethod
from uuid import UUID

from notification_service.domain.entities import Notification


class NotificationRepositoryPort(ABC):
    @abstractmethod
    def exists(self, uuid: UUID) -> bool: ...

    @abstractmethod
    def create(self, notification: Notification) -> Notification: ...

    @abstractmethod
    def get_by_uuid(self, uuid: UUID) -> Notification | None: ...


