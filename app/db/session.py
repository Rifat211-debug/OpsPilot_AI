from collections.abc import AsyncIterator
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import get_settings

settings = get_settings()


engine = create_async_engine(
    settings.DATABASE_URL,
    echo = settings.DEBUG,
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping = True,
    connect_args ={"server_settings": {"server_path": "ops_pilot"}}
)

SessionLocal = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit = True
)

async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session, scope = "function")]
StreamingSessionDep = Annotated[AsyncSession, Depends(get_session)]            