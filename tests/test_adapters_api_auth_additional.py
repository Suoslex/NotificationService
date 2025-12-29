"""Additional tests for API authentication."""

import pytest
from unittest.mock import patch
import jwt
from keycloak.exceptions import KeycloakGetError, KeycloakError
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

from notification_service.adapters.api.auth import JWTAuthentication


class TestJWTAuthenticationAdditional:
    """Additional tests for JWTAuthentication to cover edge cases."""

    @pytest.fixture
    def auth(self):
        """Create authentication instance."""
        return JWTAuthentication()

    @pytest.fixture
    def request_factory(self):
        """Create request factory."""
        return APIRequestFactory()

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.keycloak_openid")
    def test_authenticate_keycloak_get_error(
        self, mock_keycloak, mock_settings, auth, request_factory
    ):
        """Test authentication with KeycloakGetError."""
        mock_settings.JWT_KEYCLOAK_ENABLED = True

        mock_keycloak.decode_token.side_effect = KeycloakGetError(
            "User not found"
        )

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer test-token"
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.keycloak_openid")
    def test_authenticate_keycloak_general_error(
        self, mock_keycloak, mock_settings, auth, request_factory
    ):
        """Test authentication with general KeycloakError."""
        mock_settings.JWT_KEYCLOAK_ENABLED = True
        mock_settings.JWT_AUTH_ENABLED = False

        mock_keycloak.decode_token.side_effect = KeycloakError(
            "Connection error"
        )

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer test-token"
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.keycloak_openid")
    def test_authenticate_keycloak_unexpected_exception(
        self, mock_keycloak, mock_settings, auth, request_factory
    ):
        """Test authentication with unexpected exception in Keycloak."""
        mock_settings.JWT_KEYCLOAK_ENABLED = True
        mock_settings.JWT_AUTH_ENABLED = False

        mock_keycloak.decode_token.side_effect = ValueError("Unexpected error")

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer test-token"
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.jwt.decode")
    def test_authenticate_local_jwt_invalid_token(
        self, mock_jwt_decode, mock_settings, auth, request_factory
    ):
        """Test authentication with invalid JWT token."""
        mock_settings.JWT_KEYCLOAK_ENABLED = False
        mock_settings.JWT_AUTH_ENABLED = True
        mock_settings.JWT_PUBLIC_KEY = "test-key"
        mock_settings.JWT_AUDIENCE = "test-audience"
        mock_settings.JWT_ALGORITHM = "RS256"

        mock_jwt_decode.side_effect = jwt.InvalidTokenError("Invalid token")

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer invalid-token"
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.jwt.decode")
    def test_authenticate_local_jwt_expired_message(
        self, mock_jwt_decode, mock_settings, auth, request_factory
    ):
        """Test authentication with expired token."""
        mock_settings.JWT_KEYCLOAK_ENABLED = False
        mock_settings.JWT_AUTH_ENABLED = True
        mock_settings.JWT_PUBLIC_KEY = "test-key"
        mock_settings.JWT_AUDIENCE = "test-audience"
        mock_settings.JWT_ALGORITHM = "RS256"

        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError(
            "Token expired"
        )

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer expired-token"
        )

        with pytest.raises(AuthenticationFailed) as exc_info:
            auth.authenticate(request)

        assert "expired" in str(exc_info.value).lower()

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.jwt.decode")
    def test_authenticate_local_jwt_signature_error(
        self, mock_jwt_decode, mock_settings, auth, request_factory
    ):
        """Test authentication with signature error."""
        mock_settings.JWT_KEYCLOAK_ENABLED = False
        mock_settings.JWT_AUTH_ENABLED = True
        mock_settings.JWT_PUBLIC_KEY = "test-key"
        mock_settings.JWT_AUDIENCE = "test-audience"
        mock_settings.JWT_ALGORITHM = "RS256"

        mock_jwt_decode.side_effect = jwt.InvalidTokenError(
            "Invalid signature"
        )

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer bad-token"
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)
