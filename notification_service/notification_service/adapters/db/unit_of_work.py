from django.db import transaction

from loguru import logger

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
        logger.debug("Initializing DjangoUnitOfWork")
        self.notification_repo = DjangoNotificationRepository()
        logger.debug("Initialized notification repository")

    def __enter__(self) -> 'DjangoUnitOfWork':
        logger.debug("Entering DjangoUnitOfWork transaction")
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        logger.debug("Started atomic transaction")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(
            f"Exiting DjangoUnitOfWork transaction, "
            f"exception type: {exc_type}"
        )
        self._transaction.__exit__(exc_type, exc_val, exc_tb)
        if exc_type is None:
            logger.debug("Transaction completed successfully")
        else:
            logger.error(
                f"Transaction failed with exception: {exc_val}"
            )

    def commit(self) -> None:
        logger.debug("Committing transaction")
        transaction.commit()
        logger.debug("Transaction committed successfully")

    def rollback(self) -> None:
        logger.debug("Rolling back transaction")
        transaction.rollback()
        logger.debug("Transaction rolled back successfully")
