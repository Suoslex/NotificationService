from notification_service.config.settings.base import *

DEBUG = True

STATIC_ROOT = BASE_DIR / "staticfiles"

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware"
]

