from typing import List

from notif.constants import NotificationChannel
from notif.senders import EmailSender, NotificationSender, SMSSender


class UserPreference:
    def __init__(self, user_id: str, preferred_channels: List[NotificationChannel]):
        self.user_id = user_id
        self.preferred_channels = preferred_channels


class Notifier:
    def __init__(self):
        self.channel_senders = {
            NotificationChannel.EMAIL: EmailSender(),
            NotificationChannel.SMS: SMSSender(),
        }

    def notify(self, user_pref: UserPreference, message: str) -> None:
        for channel in user_pref.preferred_channels:
            sender: NotificationSender = self.channel_senders.get(channel)
            if sender:
                sender.send(
                    user_id=user_pref.user_id,
                    message=message,
                )
