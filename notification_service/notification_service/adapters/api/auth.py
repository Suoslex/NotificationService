import jwt
from django.conf import settings
from keycloak import KeycloakGetError
from loguru import logger
from keycloak.exceptions import KeycloakError
from rest_framework.request import Request
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView

from notification_service.config.keycloak import keycloak_openid
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
        logger.debug("Starting JWT authentication")
        token = self._extract_bearer_token(request)
        if token is None:
            logger.debug("No token found in request header")
            return None
        logger.debug("Token extracted, attempting to decode")
        claims = self._decode_token(token)
        if not claims:
            logger.debug("Token decoding failed, returning None")
            return None
        scopes = claims.get("scope", "")
        if isinstance(scopes, str):
            scopes = scopes.split()
        logger.debug(
            f"Successfully authenticated user "
            f"{claims['sub']} with scopes: {scopes}"
        )
        return (
            AuthContext(
                user_uuid=claims["sub"],
                scopes=set(scopes),
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
        logger.debug("Extracting bearer token from request header")
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.debug("Authorization header not found")
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            logger.debug(f"Invalid authorization header format: {auth_header}")
            return None

        scheme, token = parts
        if scheme.lower() != "bearer":
            logger.debug(f"Invalid scheme in authorization header: {scheme}")
            return None

        logger.debug("Successfully extracted bearer token")
        return token

    def _decode_token(self, token: str) -> dict | None:
        logger.debug("Decoding JWT token")
        if settings.JWT_KEYCLOAK_ENABLED:
            try:
                logger.debug("Using Keycloak to decode token")
                result = keycloak_openid.decode_token(token)
                logger.debug("Token successfully decoded with Keycloak")
                return result
            except KeycloakGetError as e:
                logger.error(f"Keycloak token validation failed: {e}")
                raise AuthenticationFailed(
                    f"Token is invalid (most likely user_id is not found)"
                )
            except KeycloakError as e:
                logger.error(f"Keycloak error during token decoding: {e}")
                raise AuthenticationFailed(f"Keycloak error: {e}")
            except Exception as e:
                logger.error(f"Couldn't decode token with keycloak: {e}")
                raise AuthenticationFailed("Invalid token")
        elif settings.JWT_AUTH_ENABLED:
            try:
                logger.debug("Using local JWT decoding")
                result = jwt.decode(
                    token,
                    settings.JWT_PUBLIC_KEY,
                    audience=settings.JWT_AUDIENCE,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                logger.debug("Token successfully decoded locally")
                return result
            except jwt.ExpiredSignatureError as e:
                logger.warning(f"Token expired: {e}")
                raise AuthenticationFailed("Token expired")
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid token: {e}")
                raise AuthenticationFailed("Invalid token")
        logger.debug("JWT authentication is not enabled")
        return None



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
        logger.debug(
            f"Checking permission "
            f"for required scope: {view.required_scope}"
        )
        if not settings.JWT_AUTH_ENABLED:
            logger.debug("JWT auth disabled, granting permission")
            return True

        auth = request.user
        logger.debug(f"Checking user: {auth}")

        if not hasattr(auth, "has"):
            logger.debug("User doesn't have 'has' method, denying permission")
            return False

        has_scope = auth.has(view.required_scope)
        logger.debug(
            f"User required scope {view.required_scope} "
            f"check: {has_scope}"
        )
        return has_scope
