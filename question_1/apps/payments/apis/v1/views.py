from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from apps.payments.schemas.payment_schema import PaymentTransactionCreate, PaymentTransactionRead
from apps.payments.services.core_service import PaymenTransactionService
from common.schemas.response import StandardResponse
from config.db import get_session

router = APIRouter()


@router.post(
    "/payments",
    response_model=StandardResponse[PaymentTransactionRead],
    status_code=status.HTTP_201_CREATED,
)
async def process_payment(
    payload: PaymentTransactionCreate,
    session: AsyncSession = Depends(get_session),
):
    service = PaymenTransactionService(session=session)
    data = await service.process_payment(
        payload=payload,
    )
    return StandardResponse(
        data=data,
    )
