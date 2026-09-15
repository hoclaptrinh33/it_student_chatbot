"""
Database Connection - Postgres via SQLAlchemy 2.0 asyncio + asyncpg
"""
from collections.abc import AsyncGenerator
from pathlib import Path
import logging
import os

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


async def _apply_sql_migrations() -> None:
    flag = os.getenv("APPLY_SQL_MIGRATIONS", "").lower()
    if flag not in {"1", "true", "yes"}:
        return
    candidates = [
        Path(os.getenv("SQL_MIGRATIONS_PATH", "")),
        Path(__file__).resolve().parents[3] / "migrations" / "002_align_rag_schema.sql",
        Path("/app/migrations/002_align_rag_schema.sql"),
    ]
    sql_path = next((p for p in candidates if p and p.is_file()), None)
    if not sql_path:
        logger.warning("APPLY_SQL_MIGRATIONS=true but 002_align_rag_schema.sql was not found")
        return
    sql = sql_path.read_text(encoding="utf-8")
    async with engine.begin() as conn:
        raw = await conn.get_raw_connection()
        driver = getattr(raw, "driver_connection", None)
        if driver is None:
            await conn.execute(text(sql))
        else:
            await driver.execute(sql)
    logger.info("Applied SQL migrations from %s", sql_path)


async def connect_to_db() -> None:
    logger.info("Connecting to Postgres")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    await _apply_sql_migrations()
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
