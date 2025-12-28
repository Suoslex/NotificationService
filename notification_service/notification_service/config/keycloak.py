from keycloak import KeycloakAdmin, KeycloakOpenID
from django.conf import settings

config = dict(
    server_url=settings.JWT_KEYCLOAK_URL,
    client_id=settings.JWT_KEYCLOAK_CLIENT_ID,
    realm_name=settings.JWT_KEYCLOAK_REALM,
    client_secret_key=settings.JWT_KEYCLOAK_SECRET_KEY,
    verify=False
)

keycloak_openid = KeycloakOpenID(**config)
keycloak_admin = KeycloakAdmin(
    username=settings.JWT_KEYCLOAK_ADMIN_LOGIN,
    password=settings.JWT_KEYCLOAK_ADMIN_PASSWORD,
    **{**config, "client_id": "admin-cli"},
)

