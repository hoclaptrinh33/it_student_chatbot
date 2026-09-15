"""
Database Connection - Postgres via SQLAlchemy 2.0 asyncio + asyncpg
"""
from collections.abc import AsyncGenerator
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def connect_to_db() -> None:
    logger.info("Connecting to Postgres")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Postgres connected")


async def close_db() -> None:
    logger.info("Closing Postgres connection")
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """One AsyncSession per FastAPI request. Commit on success; rollback on error."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
