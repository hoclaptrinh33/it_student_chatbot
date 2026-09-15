"""
Dataset Repository - Data access cho datasets
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_, select

from app.models.orm import Dataset
from app.repositories.base_repository import BaseRepository


class DatasetRepository(BaseRepository):
    """Repository cho Dataset operations"""

    def __init__(self, session):
        super().__init__(session)

    async def create_dataset(
        self,
        name: str,
        owner_id: str,
        visibility: str = "private",
    ) -> dict:
        row = Dataset(
            name=name,
            owner_id=self.parse_id(owner_id),
            visibility=visibility,
            shared_with=[],
            created_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        return self.serialize_row(row)

    async def get_by_id(self, dataset_id: str) -> Optional[dict]:
        uid = self.parse_id(dataset_id)
        if not uid:
            return None
        row = await self.session.get(Dataset, uid)
        return self.serialize_row(row)

    async def get_all(self) -> List[dict]:
        result = await self.session.execute(select(Dataset))
        return self.serialize_rows(result.scalars().all())

    async def get_by_owner(self, owner_id: str) -> List[dict]:
        uid = self.parse_id(owner_id)
        if not uid:
            return []
        result = await self.session.execute(select(Dataset).where(Dataset.owner_id == uid))
        return self.serialize_rows(result.scalars().all())

    async def get_shared_with_user(self, user_id: str) -> List[dict]:
        result = await self.session.execute(
            select(Dataset).where(
                or_(
                    Dataset.shared_with.contains([user_id]),
                    Dataset.shared_with.contains(["*"]),
                )
            )
        )
        return self.serialize_rows(result.scalars().all())

    async def share_dataset(self, dataset_id: str, user_ids: List[str]) -> bool:
        uid = self.parse_id(dataset_id)
        if not uid:
            return False
        row = await self.session.get(Dataset, uid)
        if not row:
            return False
        row.shared_with = user_ids or []
        row.updated_at = datetime.utcnow()
        await self.session.flush()
        return True

    async def delete_dataset(self, dataset_id: str) -> bool:
        uid = self.parse_id(dataset_id)
        if not uid:
            return False
        row = await self.session.get(Dataset, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True

    async def update_dataset(self, dataset_id: str, data: dict) -> Optional[dict]:
        uid = self.parse_id(dataset_id)
        if not uid:
            return None
        row = await self.session.get(Dataset, uid)
        if not row:
            return None
        payload = dict(data)
        if "owner_id" in payload:
            payload["owner_id"] = self.parse_id(payload["owner_id"]) if payload["owner_id"] else None
        payload["updated_at"] = datetime.utcnow()
        for key, value in payload.items():
            if hasattr(row, key):
                setattr(row, key, value)
        await self.session.flush()
        return self.serialize_row(row)
