"""Tests for API authentication."""

import jwt
import pytest
from unittest.mock import Mock, patch
from keycloak.exceptions import KeycloakError
from uuid import uuid4
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

from notification_service.adapters.api.auth import JWTAuthentication, HasScope
from notification_service.application.dtos.auth_context import AuthContext


class TestJWTAuthentication:
    """Tests for JWTAuthentication."""

    @pytest.fixture
    def auth(self):
        return JWTAuthentication()

    @pytest.fixture
    def request_factory(self):
        return APIRequestFactory()

    def test_extract_bearer_token_success(self, auth, request_factory):
        """Test extracting bearer token from header."""
        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer test-token-123"
        )

        token = auth._extract_bearer_token(request)

        assert token == "test-token-123"

    def test_extract_bearer_token_no_header(self, auth, request_factory):
        """Test extracting token when no Authorization header."""
        request = request_factory.get("/")

        token = auth._extract_bearer_token(request)

        assert token is None

    def test_extract_bearer_token_invalid_format(self, auth, request_factory):
        """Test extracting token with invalid format."""
        request = request_factory.get("/", HTTP_AUTHORIZATION="InvalidFormat")

        token = auth._extract_bearer_token(request)

        assert token is None

    def test_extract_bearer_token_wrong_scheme(self, auth, request_factory):
        """Test extracting token with wrong scheme."""
        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Basic test-token-123"
        )

        token = auth._extract_bearer_token(request)

        assert token is None

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.keycloak_openid")
    def test_authenticate_with_keycloak_success(
        self, mock_keycloak, mock_settings, auth, request_factory
    ):
        """Test authentication with Keycloak enabled."""
        mock_settings.JWT_KEYCLOAK_ENABLED = True
        mock_settings.JWT_AUTH_ENABLED = False

        user_uuid = uuid4()
        claims = {"sub": str(user_uuid), "scope": "read write"}
        mock_keycloak.decode_token.return_value = claims

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer test-token"
        )

        result = auth.authenticate(request)

        assert result is not None
        user, _ = result
        assert isinstance(user, AuthContext)
        assert user.user_uuid == user_uuid
        assert "read" in user.scopes
        assert "write" in user.scopes
        mock_keycloak.decode_token.assert_called_once()

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.keycloak_openid")
    def test_authenticate_with_keycloak_error(
        self, mock_keycloak, mock_settings, auth, request_factory
    ):
        """Test authentication with Keycloak error."""

        mock_settings.JWT_KEYCLOAK_ENABLED = True
        mock_settings.JWT_AUTH_ENABLED = False
        mock_keycloak.decode_token.side_effect = KeycloakError("Invalid token")

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer invalid-token"
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.jwt")
    def test_authenticate_with_local_jwt_success(
        self, mock_jwt, mock_settings, auth, request_factory
    ):
        """Test authentication with local JWT."""
        mock_settings.JWT_KEYCLOAK_ENABLED = False
        mock_settings.JWT_AUTH_ENABLED = True
        mock_settings.JWT_PUBLIC_KEY = "test-key"
        mock_settings.JWT_AUDIENCE = "test-audience"
        mock_settings.JWT_ALGORITHM = "RS256"

        user_uuid = uuid4()
        claims = {"sub": str(user_uuid), "scope": "read write"}
        mock_jwt.decode.return_value = claims

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer test-token"
        )

        result = auth.authenticate(request)

        assert result is not None
        user, _ = result
        assert isinstance(user, AuthContext)
        assert user.user_uuid == user_uuid
        mock_jwt.decode.assert_called_once()

    @patch("notification_service.adapters.api.auth.settings")
    @patch("notification_service.adapters.api.auth.jwt.decode")
    def test_authenticate_with_local_jwt_expired(
        self, mock_jwt_decode, mock_settings, auth, request_factory
    ):
        """Test authentication with expired JWT."""

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

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    @patch("notification_service.adapters.api.auth.settings")
    def test_authenticate_no_auth_enabled(
        self, mock_settings, auth, request_factory
    ):
        """Test authentication when auth is disabled."""
        mock_settings.JWT_KEYCLOAK_ENABLED = False
        mock_settings.JWT_AUTH_ENABLED = False

        request = request_factory.get(
            "/", HTTP_AUTHORIZATION="Bearer test-token"
        )

        result = auth.authenticate(request)

        assert result is None

    def test_authenticate_no_token(self, auth, request_factory):
        """Test authentication when no token provided."""
        request = request_factory.get("/")

        result = auth.authenticate(request)

        assert result is None


class TestHasScope:
    """Tests for HasScope permission."""

    @pytest.fixture
    def permission(self):
        """Create permission instance."""
        return HasScope()

    @pytest.fixture
    def request_factory(self):
        """Create request factory."""
        return APIRequestFactory()

    @pytest.fixture
    def mock_view(self):
        """Create mock view."""
        view = Mock()
        view.required_scope = "notifications:send"
        return view

    @patch("notification_service.adapters.api.auth.settings")
    def test_has_permission_auth_disabled(
        self, mock_settings, permission, request_factory, mock_view
    ):
        """Test permission check when auth is disabled."""
        mock_settings.JWT_AUTH_ENABLED = False

        request = request_factory.get("/")

        result = permission.has_permission(request, mock_view)

        assert result is True

    @patch("notification_service.adapters.api.auth.settings")
    def test_has_permission_with_scope(
        self, mock_settings, permission, request_factory, mock_view
    ):
        """Test permission check when user has required scope."""
        mock_settings.JWT_AUTH_ENABLED = True

        user = AuthContext(
            user_uuid=uuid4(), scopes={"notifications:send", "read"}
        )
        request = request_factory.get("/")
        request.user = user

        result = permission.has_permission(request, mock_view)

        assert result is True

    @patch("notification_service.adapters.api.auth.settings")
    def test_has_permission_without_scope(
        self, mock_settings, permission, request_factory, mock_view
    ):
        """Test permission check when user doesn't have required scope."""
        mock_settings.JWT_AUTH_ENABLED = True

        user = AuthContext(user_uuid=uuid4(), scopes={"read", "write"})
        request = request_factory.get("/")
        request.user = user

        result = permission.has_permission(request, mock_view)

        assert result is False

    @patch("notification_service.adapters.api.auth.settings")
    def test_has_permission_no_has_method(
        self, mock_settings, permission, request_factory, mock_view
    ):
        """Test permission check when user doesn't have has() method."""
        mock_settings.JWT_AUTH_ENABLED = True

        request = request_factory.get("/")
        mock_user = Mock()
        del mock_user.has
        request.user = mock_user

        result = permission.has_permission(request, mock_view)

        assert result is False
