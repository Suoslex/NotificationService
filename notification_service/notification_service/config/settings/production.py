from notification_service.config.settings.base import *

DEBUG = False

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1"
]