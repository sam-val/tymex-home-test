from fastapi import APIRouter

from apps.payments.apis.v1.views import router as payemnt_views

router = APIRouter()
router.include_router(payemnt_views, prefix="/v1", tags=["Payment v1"])
