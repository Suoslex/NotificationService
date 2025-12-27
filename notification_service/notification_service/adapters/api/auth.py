import jwt
from django.conf import settings
from rest_framework.request import Request
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView

from notification_service.application.dtos.auth_context import AuthContext

class JWTAuthentication(BaseAuthentication):
    """
    Class for authenticating users using JWT tokens.
    Extracts the token from the Authorization header and validates it.
    """
    def authenticate(self, request: Request):
        """
        Authenticate user based on JWT token.

        Parameters
        ----------
        request : Request
            HTTP request object containing Authorization header

        Returns
        ----------
        tuple[AuthContext, None] | None
            Tuple with authentication context and None if token is valid, 
            or just None otherwise.

        Raises
        ----------
        AuthenticationFailed
            If token is expired or invalid
        """
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

    def _extract_bearer_token(self, request: Request) -> str | None:
        """
        Extract Bearer token from Authorization header.

        Parameters
        ----------
        request : Request
            HTTP request object

        Returns
        ----------
        str | None
            Bearer token or None if token is not found or invalid format
        """
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
    """
    Class to check if a user has the required scope
    to access the protected resource. 
    Disabled when settings.JWT_AUTH_ENABLED = False.
    """
    required_scope: str

    def has_permission(self, request: Request, view: APIView):
        """
        Check if user has required scope.

        Parameters
        ----------
        request : Request
            HTTP request object
        view : APIView
            View being accessed

        Returns
        ----------
        bool
            True if user has required scope, False otherwise.
        """
        if not settings.JWT_AUTH_ENABLED:
            return True

        auth = request.user

        if not hasattr(auth, "has"):
            return False

        return auth.has(view.required_scope)
