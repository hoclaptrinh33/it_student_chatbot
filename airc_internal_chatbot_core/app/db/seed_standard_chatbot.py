"""
Standard chatbot seed is now in init_db.sql
(chatbot eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee, dataset dddddddd-...).
This script is a no-op kept for compatibility with old runbooks.
"""
import asyncio


async def seed():
    print("Seed is owned by init_db.sql — nothing to do.")
    print("Chatbot UUID: eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
    print("Dataset UUID: dddddddd-dddd-dddd-dddd-dddddddddddd")


if __name__ == "__main__":
    asyncio.run(seed())
