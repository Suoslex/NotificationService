"""Tests for adapter dependencies."""

from unittest.mock import patch

from notification_service.adapters.dependencies import (
    get_user_provider,
    get_unit_of_work,
)
from notification_service.adapters.db.unit_of_work import DjangoUnitOfWork
from notification_service.adapters.user_provider.local import LocalUserProvider
from notification_service.adapters.user_provider.keycloak import (
    KeycloakUserProvider,
)


class TestGetUserProvider:
    """Tests for get_user_provider function."""

    @patch("notification_service.adapters.dependencies.settings")
    def test_get_user_provider_keycloak_enabled(self, mock_settings):
        """Test getting Keycloak user provider when enabled."""
        mock_settings.JWT_KEYCLOAK_ENABLED = True
        mock_settings.JWT_KEYCLOAK_ADMIN_LOGIN = "admin"
        mock_settings.JWT_KEYCLOAK_ADMIN_PASSWORD = "password"

        provider = get_user_provider()

        assert isinstance(provider, KeycloakUserProvider)

    @patch("notification_service.adapters.dependencies.settings")
    def test_get_user_provider_keycloak_disabled(self, mock_settings):
        """Test getting local user provider when Keycloak is disabled."""
        mock_settings.JWT_KEYCLOAK_ENABLED = False
        mock_settings.JWT_KEYCLOAK_ADMIN_LOGIN = None
        mock_settings.JWT_KEYCLOAK_ADMIN_PASSWORD = None

        provider = get_user_provider()

        assert isinstance(provider, LocalUserProvider)

    @patch("notification_service.adapters.dependencies.settings")
    def test_get_user_provider_keycloak_no_credentials(self, mock_settings):
        """Test getting local user provider when Keycloak has no credentials"""
        mock_settings.JWT_KEYCLOAK_ENABLED = True
        mock_settings.JWT_KEYCLOAK_ADMIN_LOGIN = None
        mock_settings.JWT_KEYCLOAK_ADMIN_PASSWORD = None

        provider = get_user_provider()

        assert isinstance(provider, LocalUserProvider)


class TestGetUnitOfWork:
    """Tests for get_unit_of_work function."""

    def test_get_unit_of_work(self):
        """Test getting unit of work instance."""
        uow = get_unit_of_work()

        assert isinstance(uow, DjangoUnitOfWork)

