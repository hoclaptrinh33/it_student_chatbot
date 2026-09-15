"""
DEPRECATED Mongo debug script. Use Postgres instead, e.g.:

  psql "postgresql://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot" \\
    -c "SELECT id, name FROM chatbots; SELECT chatbot_id, dataset_id FROM chatbot_datasets;"
"""
from __future__ import annotations

import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main():
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot",
    )
    engine = create_async_engine(url, pool_pre_ping=True)
    async with engine.connect() as conn:
        bots = (await conn.execute(text("SELECT id, name FROM chatbots"))).all()
        print(f"chatbots: {len(bots)}")
        for row in bots:
            print(f" - {row.name} ({row.id})")
        links = (await conn.execute(text("SELECT chatbot_id, dataset_id FROM chatbot_datasets"))).all()
        print(f"chatbot_datasets: {len(links)}")
        for row in links:
            print(f" - {row.chatbot_id} -> {row.dataset_id}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
