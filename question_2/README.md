# Question 2
```
Using Java or Python, implement a notification system that can:
• Support multiple notification channels including Email and SMS
• Select the appropriate notification channel based on user preferences like if user enable Email as their notification option, use Email

Assumption: Email and SMS provider will be available via 3rd party providers so you don’t need to write
the actual code to send the notification through those channels
```

# 📬 Notification Module

A Python module for sending notifications based on user preferences.
- [Supports multiple channels including **Email** and **SMS**](#-multi-channel-support)
- [Selects the appropriate one(s) based on user settings](#-user-preference-handling)

> **Note:** Actual integration with Email/SMS providers is abstracted.

---

## ✅ Features

1. **Multi-channel notification support** (Email, SMS, etc.)
2. **User-configurable notification preferences**
3. Easily extensible for new channels

---

## 📚 Table of Contents

* [🚀 Quick Start](#-quick-start)
* [🧪 Running Tests](#-running-tests)
* [📱 Multi-channel Support](#-multi-channel-support)
* [👤 User Preference Handling](#-user-preference-handling)

---

## 🚀 Quick Start

### 🔧 Prerequisites

* Python `3.13`
* [`Poetry`](https://python-poetry.org/docs/#installation)
* `make` (for Makefile support)

### 📦 Installation

#### 1. Install Poetry (if you haven't installed, otherwise skip to 2):

   ```bash
   curl -sSL https://install.python-poetry.org | python3.13 -
   ```

   Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

   Then restart your shell and check:

   ```bash
   poetry --version
   ```

#### 2. Setup project environment:

   ```bash
   poetry env use python3.13
   poetry install
   ```

---

## 🧪 Running Tests

Test cases are located in `tests/test_notification.py`.

```bash
make test_all  # via Makefile
# or directly
poetry run pytest -q -rx .
```

---

## 📱 Multi-channel Support

Notification channels are defined in:

* `notif/senders.py` – contains the logic to send via Email, SMS, etc.
* `notif/constants.py` – defines the supported channel constants (e.g. `EMAIL`, `SMS`)

### Example usage:

```python
from notif.notification import Notifier, NotificationChannel, UserPreference

user_pref = UserPreference(
    user_id="user123",
    preferred_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
)

notifier = Notifier()
notifier.notify(user_pref, "Hello, this is a test message!")
```

---

## 👤 User Preference Handling

User preferences (i.e. enabled notification channels) should be loaded from your persistence layer (database, config, etc.):

```python
preferred_channels = db.get_preferred_channels(user_id)

user_pref = UserPreference(
    user_id=user_id,
    preferred_channels=preferred_channels,
)
```

If the user has disabled all notification options, the notifier will **gracefully skip** sending.

---

## 📌 Notes

* This module does **not** handle actual delivery to third-party services (e.g., Twilio, SendGrid).
* Designed to be easily integrated with FastAPI, Django, or CLI tools.
