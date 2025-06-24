# schemas.py
import uuid
from pydantic import BaseModel


class PaymentTransactionCreate(BaseModel):
    idempotency_id: str
    request_data: str


class PaymentTransactionRead(BaseModel):
    response_data: str
