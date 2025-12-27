from django.db import transaction

from notification_service.application.ports.unit_of_work import UnitOfWorkPort
from notification_service.adapters.db.repositories import (
    DjangoNotificationRepository
)


class DjangoUnitOfWork(UnitOfWorkPort):
    def __init__(self):
        self.notification_repo = DjangoNotificationRepository()

    def __enter__(self):
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._transaction.__exit__(exc_type, exc_val, exc_tb)

    def commit(self): ...

    def rollback(self): ...
