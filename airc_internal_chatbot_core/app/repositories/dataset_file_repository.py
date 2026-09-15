"""
Dataset File Repository - Data access cho dataset_files (join table)
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import delete, select

from app.models.enums import DatasetFileStatus
from app.models.orm import DatasetFile
from app.repositories.base_repository import BaseRepository


class DatasetFileRepository(BaseRepository):
    """Repository cho DatasetFile operations"""

    def __init__(self, session):
        super().__init__(session, DatasetFile)

    async def create_dataset_file(self, dataset_id: str, file_id: str) -> dict:
        ds_id = self.parse_id(dataset_id)
        f_id = self.parse_id(file_id)
        if not ds_id or not f_id:
            raise ValueError("dataset_id and file_id must be UUIDs")
        row = DatasetFile(
            dataset_id=ds_id,
            file_id=f_id,
            status=DatasetFileStatus.PENDING.value,
            chunk_count=0,
            is_enabled=True,
            created_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        return self.serialize_row(row)

    async def get_by_id(self, dataset_file_id: str) -> Optional[dict]:
        uid = self.parse_id(dataset_file_id)
        if not uid:
            return None
        row = await self.session.get(DatasetFile, uid)
        return self.serialize_row(row)

    async def get_by_dataset(self, dataset_id: str) -> List[dict]:
        uid = self.parse_id(dataset_id)
        if not uid:
            return []
        result = await self.session.execute(select(DatasetFile).where(DatasetFile.dataset_id == uid))
        return self.serialize_rows(result.scalars().all())

    async def get_enabled_by_dataset(self, dataset_id: str) -> List[dict]:
        uid = self.parse_id(dataset_id)
        if not uid:
            return []
        result = await self.session.execute(
            select(DatasetFile).where(
                DatasetFile.dataset_id == uid,
                DatasetFile.is_enabled.is_(True),
            )
        )
        return self.serialize_rows(result.scalars().all())

    async def update_status(
        self,
        dataset_file_id: str,
        status: DatasetFileStatus,
        chunk_count: Optional[int] = None,
    ) -> bool:
        uid = self.parse_id(dataset_file_id)
        if not uid:
            return False
        row = await self.session.get(DatasetFile, uid)
        if not row:
            return False
        row.status = status.value
        row.processed_at = datetime.utcnow()
        if chunk_count is not None:
            row.chunk_count = chunk_count
        await self.session.flush()
        return True

    async def set_enabled(self, dataset_file_id: str, is_enabled: bool) -> bool:
        uid = self.parse_id(dataset_file_id)
        if not uid:
            return False
        row = await self.session.get(DatasetFile, uid)
        if not row:
            return False
        row.is_enabled = is_enabled
        await self.session.flush()
        return True

    async def delete_by_id(self, dataset_file_id: str) -> bool:
        uid = self.parse_id(dataset_file_id)
        if not uid:
            return False
        row = await self.session.get(DatasetFile, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True

    async def delete_by_dataset(self, dataset_id: str) -> int:
        uid = self.parse_id(dataset_id)
        if not uid:
            return 0
        result = await self.session.execute(delete(DatasetFile).where(DatasetFile.dataset_id == uid))
        return result.rowcount or 0
