from enum import StrEnum, auto

class NotificationType(StrEnum):
    EMAIL = auto()
    SMS = auto()
    PUSH = auto()
    TELEGRAM = auto()

class NotificationStatus(StrEnum):
    PENDING = auto()
    SENT = auto()
    FAILED = auto()
