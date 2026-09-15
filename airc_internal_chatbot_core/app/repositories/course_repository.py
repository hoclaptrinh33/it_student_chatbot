"""Course repository — dict API with id as string UUID."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.models.orm import Course, StudentRecord
from app.repositories.base_repository import BaseRepository


class CourseRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)

    async def create_course(self, data: dict) -> dict:
        row = Course(
            course_code=data["course_code"],
            course_name=data["course_name"],
            credits=data["credits"],
            theory_hours=data.get("theory_hours", 0),
            practice_hours=data.get("practice_hours", 0),
            semester=data.get("semester"),
            is_mandatory=data.get("is_mandatory", True),
            career_track=data.get("career_track", "GENERAL"),
            description=data.get("description"),
            created_at=datetime.utcnow(),
        )
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ValueError(f"Course code already exists: {data['course_code']}") from exc
        return self.serialize_row(row)

    async def get_by_id(self, course_id: str) -> Optional[dict]:
        uid = self.parse_id(course_id)
        if not uid:
            return None
        row = await self.session.get(Course, uid)
        return self.serialize_row(row)

    async def get_by_code(self, course_code: str) -> Optional[dict]:
        if not course_code:
            return None
        result = await self.session.execute(
            select(Course).where(Course.course_code == course_code.strip().upper())
        )
        return self.serialize_row(result.scalar_one_or_none())

    async def get_by_id_or_code(self, value: str) -> Optional[dict]:
        found = await self.get_by_id(value)
        if found:
            return found
        return await self.get_by_code(value)

    async def list_courses(
        self,
        semester: Optional[int] = None,
        career_track: Optional[str] = None,
        q: Optional[str] = None,
        code: Optional[str] = None,
    ) -> List[dict]:
        stmt = select(Course)
        if semester is not None:
            stmt = stmt.where(Course.semester == semester)
        if career_track:
            stmt = stmt.where(Course.career_track == career_track.strip().upper())
        if code:
            stmt = stmt.where(Course.course_code == code.strip().upper())
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Course.course_code.ilike(pattern),
                    Course.course_name.ilike(pattern),
                )
            )
        stmt = stmt.order_by(Course.semester.nulls_last(), Course.course_code)
        result = await self.session.execute(stmt)
        return self.serialize_rows(result.scalars().all())

    async def update_course(self, course_id: str, data: dict) -> Optional[dict]:
        uid = self.parse_id(course_id)
        if not uid:
            return None
        row = await self.session.get(Course, uid)
        if not row:
            return None
        payload = dict(data)
        payload["updated_at"] = datetime.utcnow()
        for key, value in payload.items():
            if hasattr(row, key):
                setattr(row, key, value)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ValueError("Course code already exists") from exc
        return self.serialize_row(row)

    async def count_records(self, course_id: str) -> int:
        uid = self.parse_id(course_id)
        if not uid:
            return 0
        result = await self.session.execute(
            select(StudentRecord.id).where(StudentRecord.course_id == uid).limit(1)
        )
        return 1 if result.first() is not None else 0

    async def delete_course(self, course_id: str) -> bool:
        uid = self.parse_id(course_id)
        if not uid:
            return False
        row = await self.session.get(Course, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True
