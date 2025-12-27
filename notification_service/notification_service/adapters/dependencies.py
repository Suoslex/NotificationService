from notification_service.adapters.db.unit_of_work import DjangoUnitOfWork
from notification_service.adapters.user_provider.local import LocalUserProvider
from notification_service.application.ports.unit_of_work import UnitOfWorkPort
from notification_service.application.ports.user_provider import (
    UserProviderPort
)


def get_user_provider() -> UserProviderPort:
    return LocalUserProvider()

def get_unit_of_work() -> UnitOfWorkPort:
    return DjangoUnitOfWork()