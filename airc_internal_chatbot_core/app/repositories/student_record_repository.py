"""Student records + eligible-courses SQL function."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.models.orm import Course, StudentRecord, User
from app.repositories.base_repository import BaseRepository


class StudentRecordRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)

    def _hydrate(self, record: StudentRecord, course: Optional[Course] = None) -> dict:
        doc = self.serialize_row(record)
        if course is not None:
            doc["course_code"] = course.course_code
            doc["course_name"] = course.course_name
            doc["credits"] = course.credits
            doc["career_track"] = course.career_track
        return doc

    async def get_by_id(self, record_id: str) -> Optional[dict]:
        uid = self.parse_id(record_id)
        if not uid:
            return None
        stmt = (
            select(StudentRecord, Course)
            .join(Course, Course.id == StudentRecord.course_id)
            .where(StudentRecord.id == uid)
        )
        result = await self.session.execute(stmt)
        pair = result.first()
        if not pair:
            return None
        return self._hydrate(pair[0], pair[1])

    async def get_by_user_and_course(self, user_id: str, course_id: str) -> Optional[dict]:
        uid = self.parse_id(user_id)
        cid = self.parse_id(course_id)
        if not uid or not cid:
            return None
        result = await self.session.execute(
            select(StudentRecord).where(
                StudentRecord.user_id == uid,
                StudentRecord.course_id == cid,
            )
        )
        return self.serialize_row(result.scalar_one_or_none())

    async def list_by_user(self, user_id: str) -> List[dict]:
        uid = self.parse_id(user_id)
        if not uid:
            return []
        stmt = (
            select(StudentRecord, Course)
            .join(Course, Course.id == StudentRecord.course_id)
            .where(StudentRecord.user_id == uid)
            .order_by(StudentRecord.semester_taken.nulls_last(), Course.course_code)
        )
        result = await self.session.execute(stmt)
        return [self._hydrate(record, course) for record, course in result.all()]

    async def upsert(
        self,
        user_id: str,
        course_id: str,
        status: str,
        grade: Optional[float],
        semester_taken: Optional[str],
        attempt_count: int,
    ) -> dict:
        uid = self.parse_id(user_id)
        cid = self.parse_id(course_id)
        if not uid or not cid:
            raise ValueError("Invalid user_id or course_id")
        result = await self.session.execute(
            select(StudentRecord).where(
                StudentRecord.user_id == uid,
                StudentRecord.course_id == cid,
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.status = status
            row.grade = grade
            row.semester_taken = semester_taken
            row.attempt_count = attempt_count
            row.recorded_at = datetime.utcnow()
        else:
            row = StudentRecord(
                user_id=uid,
                course_id=cid,
                status=status,
                grade=grade,
                semester_taken=semester_taken,
                attempt_count=attempt_count,
                recorded_at=datetime.utcnow(),
            )
            self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ValueError("Could not upsert student record") from exc
        course = await self.session.get(Course, cid)
        return self._hydrate(row, course)

    async def delete(self, record_id: str) -> bool:
        uid = self.parse_id(record_id)
        if not uid:
            return False
        row = await self.session.get(StudentRecord, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True

    async def get_user(self, user_id: str) -> Optional[dict]:
        uid = self.parse_id(user_id)
        if not uid:
            return None
        row = await self.session.get(User, uid)
        return self.serialize_row(row)

    async def get_user_by_student_code(self, student_code: str) -> Optional[dict]:
        if not student_code:
            return None
        result = await self.session.execute(
            select(User).where(User.student_code == student_code.strip())
        )
        return self.serialize_row(result.scalar_one_or_none())

    async def list_eligible(self, user_id: str) -> List[dict]:
        uid = self.parse_id(user_id)
        if not uid:
            return []
        result = await self.session.execute(
            text(
                """
                SELECT course_id, course_code, course_name, credits, semester,
                       career_track, is_mandatory, missing_prereq_codes,
                       recommended_previous
                FROM fn_student_eligible_courses(:uid)
                ORDER BY semester NULLS LAST, course_code
                """
            ),
            {"uid": uid},
        )
        rows = []
        for row in result.mappings().all():
            doc = self.serialize_row(dict(row))
            doc["missing_prereq_codes"] = list(doc.get("missing_prereq_codes") or [])
            doc["recommended_previous"] = list(doc.get("recommended_previous") or [])
            rows.append(doc)
        return rows
