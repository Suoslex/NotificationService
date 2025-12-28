from notification_service.adapters.db.unit_of_work import DjangoUnitOfWork
from notification_service.adapters.user_provider.keycloak import (
    KeycloakUserProvider
)
from notification_service.application.ports.unit_of_work import UnitOfWorkPort
from notification_service.application.ports.user_provider import (
    UserProviderPort
)


def get_user_provider() -> UserProviderPort:
    """
    Get user provider instance.

    Returns
    ----------
    UserProviderPort
        Adapter implementation of UserProviderPort.
    """
    return KeycloakUserProvider()

def get_unit_of_work() -> UnitOfWorkPort:
    """
    Get unit of work instance.

    Returns
    ----------
    UnitOfWorkPort
        Adapter implementation of UnitOfWorkPort.
    """
    return DjangoUnitOfWork()