from typing import Any, Generic, Optional, Sequence, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from pydantic import BaseModel
from sqlalchemy import exc
from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select

from common.schemas.enums import OrderEnum

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Based on https://github.com/jonra1993/fastapi-alembic-sqlmodel-async
    """

    def __init__(self, model: type[ModelType], session: Optional[AsyncSession] = None):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLModel model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.session = session

    async def get(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db_session or self.session
        query = select(self.model).where(self.model.id == id)
        response = await db_session.exec(query)
        return response.one_or_none()

    async def get_by_ids(
        self,
        *,
        list_ids: list[UUID | str],
        db_session: AsyncSession | None = None,
    ) -> list[ModelType] | None:
        db_session = db_session or self.session
        response = await db_session.exec(
            select(self.model).where(self.model.id.in_(list_ids))
        )
        return response.all()

    async def get_count(self, db_session: AsyncSession | None = None) -> ModelType | None:
        db_session = db_session or self.session
        response = await db_session.exec(
            select(func.count()).select_from(select(self.model).subquery())
        )
        return response.one()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        query: T | Select[T] | None = None,
        db_session: AsyncSession | None = None,
    ) -> list[ModelType]:
        db_session = db_session or self.session
        if query is None:
            query = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        response = await db_session.exec(query)
        return response.all()

    async def get_multi_paginated(
        self,
        *,
        params: Params | None = Params(),
        query: T | Select[T] | None = None,
        db_session: AsyncSession | None = None,
    ) -> Page[ModelType]:
        db_session = db_session or self.session
        if query is None:
            query = select(self.model)

        output = await paginate(db_session, query, params)
        return output

    async def get_multi_paginated_ordered(
        self,
        *,
        params: Params | None = Params(),
        order_by: str | None = None,
        order: OrderEnum | None = OrderEnum.asc,
        query: T | Select[T] | None = None,
        db_session: AsyncSession | None = None,
    ) -> Page[ModelType]:
        db_session = db_session or self.session
        columns = self.model.__table__.columns

        if order_by is None or order_by not in columns:
            order_by = "id"

        if query is None:
            if order == OrderEnum.asc:
                query = select(self.model).order_by(columns[order_by].asc())
            else:
                query = select(self.model).order_by(columns[order_by].desc())

        return await paginate(db_session, query, params)

    async def get_multi_ordered(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order: OrderEnum | None = OrderEnum.asc,
        db_session: AsyncSession | None = None,
    ) -> list[ModelType]:
        db_session = db_session or self.session
        columns = self.model.__table__.columns

        if order_by is None or order_by not in columns:
            order_by = "id"

        if order == OrderEnum.asc:
            query = (
                select(self.model)
                .offset(skip)
                .limit(limit)
                .order_by(columns[order_by].asc())
            )
        else:
            query = (
                select(self.model)
                .offset(skip)
                .limit(limit)
                .order_by(columns[order_by].desc())
            )

        response = await db_session.exec(query)
        return response.all()

    async def create(
        self,
        *,
        obj_in: CreateSchemaType | ModelType,
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> ModelType:
        db_session = db_session or self.session

        db_obj = self.model.model_validate(obj_in)  # type: ignore

        # case there is created-by-id Field
        if created_by_id:
            db_obj.created_by_id = created_by_id

        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError:
            await db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        await db_session.refresh(db_obj)
        return db_obj

    async def bulk_create(
        self,
        *,
        objs_in: Sequence[CreateSchemaType | ModelType],
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ):
        db_session = db_session or self.session

        # case there is created-by-id Field
        db_objects = []
        for obj_in in objs_in:
            db_obj = self.model.model_validate(obj_in)  # type: ignore
            if created_by_id:
                db_obj.created_by_id = created_by_id
            db_objects.append(db_obj)

        try:
            db_session.add_all(db_objects)
            await db_session.commit()
        except exc.IntegrityError:
            await db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )

        for obj in db_objects:
            await db_session.refresh(obj)
        return db_objects

    async def update(
        self,
        *,
        obj_current: ModelType,
        obj_new: UpdateSchemaType | dict[str, Any] | ModelType,
        db_session: AsyncSession | None = None,
    ) -> ModelType:
        db_session = db_session or self.session

        if not obj_current:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource Not Found",
            )

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.model_dump(
                exclude_unset=True
            )  # This tells Pydantic to not include the values that were not sent
        for field in update_data:
            setattr(obj_current, field, update_data[field])

        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current

    async def remove(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> ModelType:
        db_session = db_session or self.session
        response = await db_session.exec(select(self.model).where(self.model.id == id))
        obj = response.one_or_none()
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource Not Found",
            )

        await db_session.delete(obj)
        await db_session.commit()
        return obj
