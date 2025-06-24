from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from apps.payments.models import IdempotencyKey
from apps.payments.schemas import PaymentTransactionCreate, PaymentTransactionRead
from common.repository.base import CRUDBase


class IdempotencyKeyRepo(CRUDBase[IdempotencyKey, PaymentTransactionRead, PaymentTransactionCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(IdempotencyKey, session=session)

    async def get_by_idempotency_id(self, idempotency_id: str) -> IdempotencyKey:
        query = select(self.model).where(self.model.key == idempotency_id)
        result = await self.session.exec(query)
        return result.one_or_none()

    async def store_request_data(
        self, payload: PaymentTransactionCreate, response_data: str
    ):
        # we have db constaints (idempotency as primary key)
        # so concurrency already handled
        obj_in = IdempotencyKey(
            key=payload.idempotency_id,
            request_data=payload.request_data,
            response_data=response_data,
        )
        result = await self.create(obj_in=obj_in)
        return result
