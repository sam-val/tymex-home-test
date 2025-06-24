# Question 2
```
Using Java or Python, implement a notification system that can:
• Support multiple notification channels including Email and SMS
• Select the appropriate notification channel based on user preferences like if user enable Email as their notification option, use Email

Assumption: Email and SMS provider will be available via 3rd party providers so you don’t need to write
the actual code to send the notification through those channels
```

# Notification Module 

Python module (not api related) to satisfy the requirements:

1. [Support multiple notification channels including Email and SMS](#multi-channel-senders-support)
2. [Select the appropriate notification channel based on user preferences like if user enable Email as their notification option, use Email](#handle-multiple-options)
## 📚 Table of Contents

- [️🚀 Quick Start](#️-quick-start)
- [🧪️ Running Tests](#run-tests)
- [🛠️ Multi-channel Support](#multi-channel-senders-support)
- [👤 Multiple User Options](#handle-multiple-options)

## 🛠️ Quick Start
### 🔧 Prerequisites
- Python 3.13
- Poetry
- make (for Makefile support)

### 🔧 Install Poetry

If you don't have Poetry, install it using the [official instructions](https://python-poetry.org/docs/#installation). For most systems, this works:

**MacOS/Linux:**

```bash
curl -sSL https://install.python-poetry.org | python3.13 -
```

You may need to restart your shell or manually add Poetry to your PATH. Add the following to your .bashrc, .zshrc, or equivalent:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then restart your terminal and verify it works:

```bash
poetry --version
```

### 🔧 Init dependencies 
```bash
# at root dir
poetry env use python3.13
poetry install
```

## Run Tests

Tests are at: `tests/test_notification.py`

```bash
make test_all # (with make)
# or
poetry run poetry run pytest -q -rx .
```

## Multi-channel (senders) support

Channels/Senders are defined in `notif/senders.py`

Constants for channels are setup in `notif/constants.py`

If user has multiple perferred channels, we can setup like:
```python
pref = UserPreference(
    user_id=user_id,
    preferred_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
)
```
And use it with `Notifier` class to send the notif
```python
notifier = Notifier()
notifier.notify(pref, message)
```

## Handle multiple options 
For their enable notif options, we can get their options (probably stored on a persistence layer)

And pass it into this module, something like:
```python
preferred_channels = db.get_preferred_channels()  # hit db 

pref = UserPreference(
    user_id=user_id,
    preferred_channels=preferred_channels,
)
```

If they disable all notif options, this won't run. This module allows flexbility for users choices.
