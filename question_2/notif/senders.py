
from typing import Protocol


class NotificationSender(Protocol):
    def send(self, user_id: str, message: str) -> None:
        ...


class EmailSender:
    def send(self, user_id: str, message: str) -> None:
        """
        Third party implementation
        """
        ...


class SMSSender:
    def send(self, user_id: str, message: str) -> None:
        """
        Third party implementation
        """
        ...
