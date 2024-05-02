from typing import Annotated, AsyncGenerator
from fastapi import Depends

from .settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


connect_args = {"check_same_thread": False}

engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=False,
    future=True,
    pool_size=settings.CONN_POOL_SIZE,
    pool_pre_ping=True
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    yield async_sessionmaker(engine, expire_on_commit=False)


ASession = Annotated[async_sessionmaker[AsyncSession], Depends(get_async_session)]