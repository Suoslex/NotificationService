"""
Django settings for testing.
Uses SQLite in-memory database for faster tests.
"""
from notification_service.config.settings.base import *

# Override database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
MIGRATION_MODULES = {
    'notification_service.adapters.db': None,
}

# Disable authentication for tests (unless explicitly tested)
JWT_AUTH_ENABLED = False
JWT_KEYCLOAK_ENABLED = False

# Disable notifications for tests
EMAIL_NOTIFICATIONS_ENABLED = False
SMS_NOTIFICATIONS_ENABLED = False
PUSH_NOTIFICATIONS_ENABLED = False
TELEGRAM_NOTIFICATIONS_ENABLED = False


