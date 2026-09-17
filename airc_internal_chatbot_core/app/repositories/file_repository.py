"""
File Repository - Data access cho files
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select

from app.models.enums import FileStatus
from app.models.orm import File
from app.repositories.base_repository import BaseRepository


class FileRepository(BaseRepository):
    """Repository cho File operations"""

    def __init__(self, session):
        super().__init__(session)

    async def create_file(
        self,
        name: str,
        size: int,
        mime_type: str,
        path: str,
        status: FileStatus = FileStatus.PENDING,
    ) -> dict:
        row = File(
            name=name,
            size=size,
            mime_type=mime_type,
            path=path,
            status=status.value,
            uploaded_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        return self.serialize_row(row)

    async def get_by_id(self, file_id: str) -> Optional[dict]:
        uid = self.parse_id(file_id)
        if not uid:
            return None
        row = await self.session.get(File, uid)
        return self.serialize_row(row)

    async def get_by_name(self, name: str) -> Optional[dict]:
        clean_name = name.strip()
        result = await self.session.execute(
            select(File).where(File.name.ilike(clean_name)).limit(1)
        )
        row = result.scalar_one_or_none()
        return self.serialize_row(row) if row else None

    async def get_by_id_or_name(self, identifier: str) -> Optional[dict]:
        if not identifier:
            return None
        from urllib.parse import unquote
        clean_id = unquote(identifier.strip())
        uid = self.parse_id(clean_id)
        if uid:
            row = await self.session.get(File, uid)
            if row:
                return self.serialize_row(row)
        return await self.get_by_name(clean_id)

    async def get_by_ids(self, file_ids: List[str]) -> List[dict]:
        uids = [uid for uid in (self.parse_id(fid) for fid in file_ids) if uid]
        if not uids:
            return []
        result = await self.session.execute(select(File).where(File.id.in_(uids)))
        return self.serialize_rows(result.scalars().all())

    async def update_status(
        self,
        file_id: str,
        status: FileStatus,
        error: Optional[str] = None,
    ) -> bool:
        uid = self.parse_id(file_id)
        if not uid:
            return False
        row = await self.session.get(File, uid)
        if not row:
            return False
        row.status = status.value
        row.processed_at = datetime.utcnow()
        if error:
            row.error = error
        await self.session.flush()
        return True

    async def get_ready_files(self) -> List[dict]:
        result = await self.session.execute(select(File).where(File.status == FileStatus.READY.value))
        return self.serialize_rows(result.scalars().all())

    async def get_all(self) -> List[dict]:
        result = await self.session.execute(select(File).order_by(File.uploaded_at.desc()))
        return self.serialize_rows(result.scalars().all())
