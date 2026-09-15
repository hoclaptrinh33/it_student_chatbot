"""Apply additive SQL migrations against DATABASE_URL (asyncpg)."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import asyncpg


def _dsn() -> str:
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot",
    )
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


async def apply_sql_migrations(sql_path: Path | None = None) -> None:
    path = sql_path or Path(__file__).with_name("002_align_rag_schema.sql")
    sql = path.read_text(encoding="utf-8")
    conn = await asyncpg.connect(_dsn())
    try:
        await conn.execute(sql)
        print(f"Applied {path}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(apply_sql_migrations())
