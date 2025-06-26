from fastapi import APIRouter, Depends, status, Response
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
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    service = PaymenTransactionService(session=session)
    is_created, data = await service.process_payment(
        payload=payload,
    )

    if not is_created:
        response.status_code = status.HTTP_200_OK

    return StandardResponse(
        data=data,
    )
