"""Learning materials list/bind."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select

from app.models.orm import LearningMaterial
from app.repositories.base_repository import BaseRepository


class LearningMaterialRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)

    async def list_materials(
        self,
        course_id: Optional[str] = None,
        material_type: Optional[str] = None,
    ) -> List[dict]:
        stmt = select(LearningMaterial)
        cid = self.parse_id(course_id) if course_id else None
        if cid:
            stmt = stmt.where(LearningMaterial.course_id == cid)
        if material_type:
            stmt = stmt.where(LearningMaterial.material_type == material_type.strip().upper())
        stmt = stmt.order_by(LearningMaterial.created_at.desc())
        result = await self.session.execute(stmt)
        return self.serialize_rows(result.scalars().all())

    async def get_by_id(self, material_id: str) -> Optional[dict]:
        uid = self.parse_id(material_id)
        if not uid:
            return None
        row = await self.session.get(LearningMaterial, uid)
        return self.serialize_row(row)

    async def create_material(self, data: dict) -> dict:
        row = LearningMaterial(
            course_id=self.parse_id(data["course_id"]),
            title=data["title"],
            material_type=data["material_type"],
            file_url=data.get("file_url"),
            file_id=self.parse_id(data["file_id"]) if data.get("file_id") else None,
            dataset_id=self.parse_id(data["dataset_id"]) if data.get("dataset_id") else None,
            created_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        return self.serialize_row(row)

    async def update_material(self, material_id: str, data: dict) -> Optional[dict]:
        uid = self.parse_id(material_id)
        if not uid:
            return None
        row = await self.session.get(LearningMaterial, uid)
        if not row:
            return None
        payload = dict(data)
        if "course_id" in payload and payload["course_id"]:
            payload["course_id"] = self.parse_id(payload["course_id"])
        if "file_id" in payload:
            payload["file_id"] = self.parse_id(payload["file_id"]) if payload["file_id"] else None
        if "dataset_id" in payload:
            payload["dataset_id"] = self.parse_id(payload["dataset_id"]) if payload["dataset_id"] else None
        for key, value in payload.items():
            if hasattr(row, key):
                setattr(row, key, value)
        await self.session.flush()
        return self.serialize_row(row)
