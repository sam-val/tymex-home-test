from enum import Enum


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
