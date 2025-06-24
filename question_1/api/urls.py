from fastapi import APIRouter

from apps.payments.apis.v1 import router as payment_router_v1

api_router = APIRouter()

api_router.include_router(payment_router_v1, prefix="/payment")
