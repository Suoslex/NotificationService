from django.conf import settings
from loguru import logger

from notification_service.adapters.db.unit_of_work import DjangoUnitOfWork
from notification_service.adapters.user_provider.keycloak import (
    KeycloakUserProvider
)
from notification_service.adapters.user_provider.local import LocalUserProvider
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
    if (
        settings.JWT_KEYCLOAK_ENABLED
        and settings.JWT_KEYCLOAK_ADMIN_LOGIN
        and settings.JWT_KEYCLOAK_ADMIN_PASSWORD
    ):
        logger.info("Keycloak is enabled as UserProvider.")
        return KeycloakUserProvider()
    logger.info("Keycloak is not available as UserProvider. Using Local.")
    return LocalUserProvider()

def get_unit_of_work() -> UnitOfWorkPort:
    """
    Get unit of work instance.

    Returns
    ----------
    UnitOfWorkPort
        Adapter implementation of UnitOfWorkPort.
    """
    return DjangoUnitOfWork()