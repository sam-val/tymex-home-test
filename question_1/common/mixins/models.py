from datetime import datetime

from sqlmodel import Field


class TimestampMixin:
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
