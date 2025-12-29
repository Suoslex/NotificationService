from notification_service.config.settings.base import *

DEBUG = True

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware"
]

