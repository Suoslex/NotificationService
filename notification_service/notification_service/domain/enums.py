from enum import StrEnum, auto

class NotificationType(StrEnum):
    """
    Enum for notification types.
    Defines the different types of notifications that can be sent.
    """
    EMAIL = auto()
    SMS = auto()
    PUSH = auto()
    TELEGRAM = auto()

class NotificationStatus(StrEnum):
    """
    Enum for notification statuses.
    Defines the different statuses that a notification can have.
    """
    PENDING = auto()
    SENT = auto()
    FAILED = auto()
