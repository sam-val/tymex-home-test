from unittest.mock import MagicMock, patch

from notif.notification import Notifier, NotificationChannel, UserPreference


@patch("notif.notification.SMSSender")
@patch("notif.notification.EmailSender")
def test_notify_no_options(mock_email_sender, mock_sms_sender):
    mock_sms_obj = MagicMock()
    mock_email_obj = MagicMock()
    mock_sms_sender.return_value = mock_sms_obj
    mock_email_sender.return_value = mock_email_obj

    user_id = "user_1"
    message = "test message"
    channels = []
    user = UserPreference(user_id, channels)

    notifier = Notifier()
    notifier.notify(user, message)

    mock_sms_obj.send.assert_not_called()
    mock_email_obj.send.assert_not_called()


@patch("notif.notification.EmailSender")
def test_notify_email_only(mock_email_sender):
    mock_obj = MagicMock()
    mock_email_sender.return_value = mock_obj
    user_id = "user_1"
    message = "test message"
    channels = [NotificationChannel.EMAIL]
    user = UserPreference(user_id, channels)

    notifier = Notifier()
    notifier.notify(user, message)

    mock_obj.send.assert_called_once_with(
        user_id=user_id,
        message=message,
    )


@patch("notif.notification.SMSSender")
def test_notify_sms_only(mock_sms_sender):
    mock_obj = MagicMock()
    mock_sms_sender.return_value = mock_obj
    user_id = "user_1"
    message = "test message"
    channels = [NotificationChannel.SMS]
    user = UserPreference(user_id, channels)

    notifier = Notifier()
    notifier.notify(user, message)

    mock_obj.send.assert_called_once_with(
        user_id=user_id,
        message=message,
    )


@patch("notif.notification.SMSSender")
@patch("notif.notification.EmailSender")
def test_notify_multiple_channels(mock_email_sender, mock_sms_sender):
    """
    If there are multiple prefer channels, send to first prefered 
    """
    mock_sms_obj = MagicMock()
    mock_email_obj = MagicMock()
    mock_sms_sender.return_value = mock_sms_obj
    mock_email_sender.return_value = mock_email_obj
    message = "mutil channel test"
    user_id = "3"

    pref = UserPreference(
        user_id=user_id,
        preferred_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
    )

    notifier = Notifier()
    notifier.notify(pref, message)

    mock_email_obj.send.assert_called_once_with(
        user_id=user_id,
        message=message,
    )
    mock_sms_obj.send.assert_called_once_with(
        user_id=user_id,
        message=message,
    )
