from abc import ABC, abstractmethod

from notification_service.application.ports.repositories import (
    NotificationRepositoryPort
)

class UnitOfWorkPort(ABC):
    """
    Abstract base class for unit of work port.
    Defines the interface for transaction management operations.
    """
    notification_repo: NotificationRepositoryPort

    @abstractmethod
    def __enter__(self) -> 'UnitOfWorkPort':
        """
        Enter the transaction context.

        Returns
        ----------
        UnitOfWorkPort
            Instance of the unit of work
        """
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the transaction context.

        Parameters
        ----------
        exc_type : type
            Exception type if any occurred
        exc_val : Exception
            Exception instance if any occurred
        exc_tb : traceback
            Traceback if any occurred
        """
        ...

    @abstractmethod
    def commit(self) -> None:
        """
        Commit the transaction.

        Raises
        ----------
        NotImplementedError
            Method is not implemented
        """
        ...

    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback the transaction.

        Raises
        ----------
        NotImplementedError
            Method is not implemented
        """
        ...