"""Data access for the singleton / LLM system settings rows."""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.orm import SystemSetting
from app.repositories.base_repository import BaseRepository

LLM_SETTINGS_ID = "llm"


class SystemSettingsRepository:
    def __init__(self, session):
        self.session = session

    def _flatten(self, row: SystemSetting) -> dict:
        data = dict(row.config or {})
        data["id"] = row.id
        data["_id"] = row.id
        data["updated_at"] = row.updated_at
        return BaseRepository.serialize_row(data)

    async def get_llm(self) -> Optional[dict]:
        row = await self.session.get(SystemSetting, LLM_SETTINGS_ID)
        if not row:
            return None
        return self._flatten(row)

    async def upsert_llm(self, data: Dict[str, Any]) -> dict:
        payload = dict(data)
        payload.pop("id", None)
        payload.pop("_id", None)
        payload.pop("updated_at", None)
        now = datetime.utcnow()
        stmt = (
            pg_insert(SystemSetting)
            .values(id=LLM_SETTINGS_ID, config=payload, updated_at=now)
            .on_conflict_do_update(
                index_elements=["id"],
                set_={"config": payload, "updated_at": now},
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()
        doc = await self.get_llm()
        return doc or {"id": LLM_SETTINGS_ID, **payload, "updated_at": now}
