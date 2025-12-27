import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from notification_service.application.dtos.auth_context import AuthContext

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = self._extract_bearer_token(request)
        if token is None:
            return None

        try:
            claims = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY,
                audience=settings.JWT_AUDIENCE,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        return (
            AuthContext(
                user_id=claims["sub"],
                scopes=set(claims.get("scope", "").split()),
            ),
            None,
        )

    def _extract_bearer_token(self, request) -> str | None:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            return None

        scheme, token = parts
        if scheme.lower() != "bearer":
            return None

        return token


class HasScope(BasePermission):
    required_scope: str

    def has_permission(self, request, view):
        if not settings.JWT_AUTH_ENABLED:
            return True

        auth = request.user

        if not hasattr(auth, "has"):
            return False

        return auth.has(view.required_scope)
