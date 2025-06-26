from datetime import datetime, timedelta
import pytest
from httpx import ASGITransport, AsyncClient

from apps.payments.models.payment import IdempotencyKey
from apps.payments.repositories import IdempotencyKeyRepo
from main import app


class TestPaymentV1:
    @pytest.mark.asyncio
    async def test_process_payment_api_case_no_idempotency(self, db_session):
        async with AsyncClient(transport= ASGITransport(app), base_url="http://test") as ac:
            res = await ac.post("/api/payment/v1/payments", json={
                "request_data": "request_data",
                "idempotency_id": "1"
            })
            assert res.status_code == 201
            assert type(res.json()["data"]["response_data"]) == str 
            assert res.json()["data"]["response_data"] is not None

            repo = IdempotencyKeyRepo(session=db_session)
            key = await repo.get_by_idempotency_id("1")
            assert key is not None
            assert key.request_data == "request_data"


    @pytest.mark.asyncio
    async def test_process_payment_api_case_existing_idempotency(self, db_session):
        # create and hit with another request with same idempotency
        obj_in = IdempotencyKey(
            key="1",
            request_data="request",
            response_data="response",
        )
        repo = IdempotencyKeyRepo(session=db_session)
        await repo.create(obj_in=obj_in)

        async with AsyncClient(transport= ASGITransport(app), base_url="http://test") as ac:
            res = await ac.post("/api/payment/v1/payments", json={
                "request_data": "request_data",
                "idempotency_id": "1"
            })
            assert res.status_code == 201
            assert type(res.json()["data"]["response_data"]) == str 
            assert res.json()["data"]["response_data"] is not None


    @pytest.mark.asyncio
    async def test_process_payment_api_case_expired_idempotency(self, db_session):
        # create and hit with another request with same idempotency
        obj_in = IdempotencyKey(
            key="1",
            request_data="request",
            response_data="response",
            expires_at=datetime.now() - timedelta(seconds=10),
        )
        repo = IdempotencyKeyRepo(session=db_session)
        await repo.create(obj_in=obj_in)

        async with AsyncClient(transport= ASGITransport(app), base_url="http://test") as ac:
            res = await ac.post("/api/payment/v1/payments", json={
                "request_data": "request_data",
                "idempotency_id": "1"
            })
            assert res.status_code == 409
