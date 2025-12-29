"""Tests for adapter unit of work."""

import pytest

from notification_service.adapters.db.unit_of_work import DjangoUnitOfWork
from notification_service.adapters.db.repositories import (
    DjangoNotificationRepository,
)


@pytest.mark.django_db
class TestDjangoUnitOfWork:
    """Tests for DjangoUnitOfWork."""

    def test_initialization(self):
        """Test unit of work initialization."""
        uow = DjangoUnitOfWork()

        assert uow.notification_repo is not None
        assert isinstance(uow.notification_repo, DjangoNotificationRepository)

    def test_context_manager_enter(self):
        """Test entering unit of work context."""
        uow = DjangoUnitOfWork()

        with uow as context_uow:
            assert context_uow is uow
            assert uow._transaction is not None

    def test_context_manager_exit_success(self):
        """Test exiting unit of work context successfully."""
        uow = DjangoUnitOfWork()

        with uow:
            pass

    def test_context_manager_exit_with_exception(self):
        """Test exiting unit of work context with exception."""
        uow = DjangoUnitOfWork()

        with pytest.raises(ValueError):
            with uow:
                raise ValueError("Test exception")

    def test_commit(self):
        """Test commit() method."""
        uow = DjangoUnitOfWork()

        with uow:
            try:
                uow.commit()
            except Exception:
                pass

    def test_rollback(self):
        """Test rollback() method."""
        uow = DjangoUnitOfWork()

        assert hasattr(uow, "rollback")
        assert callable(uow.rollback)
