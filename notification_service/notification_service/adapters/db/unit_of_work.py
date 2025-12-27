from django.db import transaction

from notification_service.application.ports.unit_of_work import UnitOfWorkPort
from notification_service.adapters.db.repositories import (
    DjangoNotificationRepository
)


class DjangoUnitOfWork(UnitOfWorkPort):
    """
    Unit of work implementation using Django transaction management.
    Manages database transactions and provides repositories for data access.
    """
    def __init__(self):
        self.notification_repo = DjangoNotificationRepository()

    def __enter__(self) -> 'DjangoUnitOfWork':
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._transaction.__exit__(exc_type, exc_val, exc_tb)

    def commit(self) -> None:
        """
        Commit the transaction.

        Raises
        ----------
        NotImplementedError
            Method is not implemented
        """
        transaction.commit()

    def rollback(self) -> None:
        """
        Rollback the transaction.

        Raises
        ----------
        NotImplementedError
            Method is not implemented
        """
        transaction.rollback()
