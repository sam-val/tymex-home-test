from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool
from sqlmodel.ext.asyncio.session import AsyncSession

from config.settings import ModeEnum, get_settings

settings = get_settings()

engine = create_engine(
    url=str(settings.ASYNC_SQLITE_URI),
    echo=settings.DEBUG,
)

async_engine = create_async_engine(
    url=str(settings.ASYNC_SQLITE_URI),
    echo=settings.DEBUG,
    poolclass=(
        NullPool if settings.MODE == ModeEnum.testing else AsyncAdaptedQueuePool
    ),  # Asincio pytest works with NullPool
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session: AsyncSession = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
