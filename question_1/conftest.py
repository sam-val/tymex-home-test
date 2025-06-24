# conftest.py
import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from config.settings import get_settings

settings = get_settings()


@pytest.fixture(scope="session")
async def async_db_engine():
    async_engine = create_async_engine(
        url=str(settings.ASYNC_UNITEST_SQLITE_URI),
        echo=True,
        poolclass=NullPool,  # Asincio pytest works with NullPool
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest.fixture(scope="function")
async def db_session(async_db_engine):
    async_session = sessionmaker(
        async_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


# make sure each test has clean tables
@pytest.fixture(autouse=True)
async def truncate_tables(async_db_engine):
    async with async_db_engine.begin() as conn:
        for table in reversed(SQLModel.metadata.sorted_tables):
            await conn.execute(table.delete())
