from datetime import datetime, timedelta

from sqlmodel import Field, SQLModel

from apps.payments.constants import IDEMPOTENCY_EXPIRY_SECONDS


class IdempotencyKey(SQLModel, table=True):
    key: str = Field(primary_key=True)
    request_data: str  # for this test, simplify data as string
    response_data: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(seconds=IDEMPOTENCY_EXPIRY_SECONDS)
    )
