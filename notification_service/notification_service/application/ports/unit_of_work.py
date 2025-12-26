from abc import ABC, abstractmethod

from notification_service.application.ports.repositories import (
    NotificationRepositoryPort
)

class UnitOfWorkPort(ABC):
    notification_repo: NotificationRepositoryPort

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...