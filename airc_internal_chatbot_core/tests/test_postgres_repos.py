"""parse_id, serialize_row, and ChatbotRepository.dataset_ids hydrate (no live Postgres)."""
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.repositories.base_repository import BaseRepository
from app.repositories.chatbot_repository import ChatbotRepository

CHATBOT_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
DATASET_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
MONGO_OID = "507f1f77bcf86cd799439011"


def test_parse_id_accepts_seed_uuid():
    assert BaseRepository.parse_id(CHATBOT_ID) == UUID(CHATBOT_ID)
    assert BaseRepository.parse_id(DATASET_ID) == UUID(DATASET_ID)
    assert BaseRepository.parse_id("cccccccc-cccc-cccc-cccc-cccccccccccc") == UUID(
        "cccccccc-cccc-cccc-cccc-cccccccccccc"
    )


def test_parse_id_rejects_mongo_objectid():
    assert BaseRepository.parse_id(MONGO_OID) is None
    assert BaseRepository.parse_id("abc") is None
    assert BaseRepository.parse_id(None) is None


def test_serialize_row_converts_uuid_and_decimal():
    doc = BaseRepository.serialize_row({
        "id": UUID(CHATBOT_ID),
        "dataset_ids": [UUID(DATASET_ID)],
        "grade": Decimal("8.50"),
    })
    assert doc["id"] == CHATBOT_ID
    assert doc["dataset_ids"] == [DATASET_ID]
    assert doc["grade"] == 8.5


class FakeChatbot:
    def __init__(self):
        self.id = UUID(CHATBOT_ID)
        self.name = "Cố vấn Học tập Khoa CNTT"
        self.description = "RAG"
        self.icon = None
        self.owner_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        self.visibility = "public"
        self.allowed_roles = ["student", "teacher", "admin"]
        self.allowed_user_ids = []
        self.allowed_departments = []
        self.config = {"search_mode": "hybrid"}
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = None


@pytest.mark.asyncio
async def test_chatbot_get_by_id_hydrates_dataset_ids():
    session = AsyncMock()
    session.get = AsyncMock(return_value=FakeChatbot())
    result = MagicMock()
    result.all.return_value = [(UUID(DATASET_ID),)]
    session.execute = AsyncMock(return_value=result)

    repo = ChatbotRepository(session)
    doc = await repo.get_by_id(CHATBOT_ID)

    assert doc is not None
    assert doc["id"] == CHATBOT_ID
    assert "dataset_ids" in doc
    assert doc["dataset_ids"] == [DATASET_ID]


@pytest.mark.asyncio
async def test_chatbot_get_by_id_rejects_mongo_objectid():
    session = AsyncMock()
    repo = ChatbotRepository(session)
    doc = await repo.get_by_id(MONGO_OID)
    assert doc is None
    session.get.assert_not_called()
