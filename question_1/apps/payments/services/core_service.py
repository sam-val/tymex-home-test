"""
Business rules for writing operations, uses repo
"""

from datetime import datetime
import factory
import faker

from sqlmodel.ext.asyncio.session import AsyncSession
from apps.payments.schemas import (
    PaymentTransactionCreate,
    PaymentTransactionRead,
)
from apps.payments.repositories.payment_repo import IdempotencyKeyRepo
from apps.payments.models.payment import IdempotencyKey


class PaymenTransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = IdempotencyKeyRepo(session=session)

    @property
    def model(self) -> IdempotencyKey:
        return self.repo.model

    def calculate_response(self) -> str:
        """
        For this test, I'll return some random values
        """
        fake = faker.Faker()
        return fake.name()

    def is_expired(self, expires_at: datetime) -> bool:
        now = datetime.now()
        return now > expires_at

    async def process_payment(
        self,
        payload: PaymentTransactionCreate,
    ) -> PaymentTransactionRead:
        """
        Try to find record with itempotency
        If exists and not expire yet, return existing response
        else process and return response
        """

        idempotency_data = await self.repo.get_by_idempotency_id(
            idempotency_id=payload.idempotency_id,
        )

        if idempotency_data and not self.is_expired(idempotency_data.expires_at):
            return idempotency_data

        response_data = self.calculate_response()
        print("response data: ", response_data)
        return await self.repo.store_request_data(
            payload=payload,
            response_data=response_data,
        )
