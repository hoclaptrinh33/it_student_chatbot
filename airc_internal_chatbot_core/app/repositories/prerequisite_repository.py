"""Prerequisite edges + closure view."""
from typing import List

from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError

from app.models.orm import Course, CoursePrerequisite
from app.repositories.base_repository import BaseRepository


class PrerequisiteRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)

    async def list_direct(self, course_id: str) -> List[dict]:
        uid = self.parse_id(course_id)
        if not uid:
            return []
        stmt = (
            select(CoursePrerequisite, Course)
            .join(Course, Course.id == CoursePrerequisite.prerequisite_course_id)
            .where(CoursePrerequisite.course_id == uid)
            .order_by(CoursePrerequisite.relation_type, Course.course_code)
        )
        result = await self.session.execute(stmt)
        out = []
        for edge, course in result.all():
            doc = self.serialize_row(edge)
            doc["prerequisite_code"] = course.course_code
            doc["prerequisite_name"] = course.course_name
            out.append(doc)
        return out

    async def list_closure(self, course_id: str) -> List[dict]:
        uid = self.parse_id(course_id)
        if not uid:
            return []
        result = await self.session.execute(
            text(
                """
                SELECT course_id, course_code, course_name,
                       prerequisite_course_id, prerequisite_code, prerequisite_name,
                       relation_type, depth
                FROM v_course_prerequisite_closure
                WHERE course_id = :cid
                ORDER BY depth, prerequisite_code
                """
            ),
            {"cid": uid},
        )
        return [self.serialize_row(dict(row)) for row in result.mappings().all()]

    async def list_closure_by_code(self, course_code: str) -> List[dict]:
        if not course_code:
            return []
        result = await self.session.execute(
            text(
                """
                SELECT course_id, course_code, course_name,
                       prerequisite_course_id, prerequisite_code, prerequisite_name,
                       relation_type, depth
                FROM v_course_prerequisite_closure
                WHERE course_code = :code
                ORDER BY depth, prerequisite_code
                """
            ),
            {"code": course_code.strip().upper()},
        )
        return [self.serialize_row(dict(row)) for row in result.mappings().all()]

    async def add_edge(
        self,
        course_id: str,
        prerequisite_course_id: str,
        relation_type: str,
    ) -> dict:
        cid = self.parse_id(course_id)
        pid = self.parse_id(prerequisite_course_id)
        if not cid or not pid:
            raise ValueError("Invalid course id")
        if cid == pid:
            raise ValueError("A course cannot be a prerequisite of itself")
        row = CoursePrerequisite(
            course_id=cid,
            prerequisite_course_id=pid,
            relation_type=relation_type,
        )
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ValueError("Prerequisite edge already exists or course is missing") from exc
        return self.serialize_row(row)

    async def delete_edge(self, course_id: str, prerequisite_course_id: str) -> int:
        cid = self.parse_id(course_id)
        pid = self.parse_id(prerequisite_course_id)
        if not cid or not pid:
            return 0
        result = await self.session.execute(
            delete(CoursePrerequisite).where(
                CoursePrerequisite.course_id == cid,
                CoursePrerequisite.prerequisite_course_id == pid,
            )
        )
        await self.session.flush()
        return int(result.rowcount or 0)

    async def list_blocked(self, user_id: str, limit: int = 10) -> List[dict]:
        uid = self.parse_id(user_id)
        if not uid:
            return []
        result = await self.session.execute(
            text(
                """
                SELECT c.id AS course_id,
                       c.course_code,
                       c.course_name,
                       c.credits,
                       c.career_track,
                       'PREREQUISITE' AS relation_type,
                       ARRAY_AGG(pc.course_code ORDER BY pc.course_code)
                           FILTER (WHERE sr.status IS DISTINCT FROM 'PASSED')
                           AS missing_prereq_codes
                FROM courses c
                JOIN course_prerequisites cp
                    ON cp.course_id = c.id AND cp.relation_type = 'PREREQUISITE'
                JOIN courses pc ON pc.id = cp.prerequisite_course_id
                LEFT JOIN student_records sr
                    ON sr.course_id = cp.prerequisite_course_id
                   AND sr.user_id = :uid
                LEFT JOIN student_records mine
                    ON mine.course_id = c.id AND mine.user_id = :uid
                WHERE mine.status IS NULL OR mine.status = 'FAILED'
                GROUP BY c.id, c.course_code, c.course_name, c.credits, c.career_track
                HAVING COUNT(*) FILTER (WHERE sr.status IS DISTINCT FROM 'PASSED') > 0
                ORDER BY c.semester NULLS LAST, c.course_code
                LIMIT :lim
                """
            ),
            {"uid": uid, "lim": limit},
        )
        rows = []
        for row in result.mappings().all():
            doc = self.serialize_row(dict(row))
            doc["missing_prereq_codes"] = list(doc.get("missing_prereq_codes") or [])
            rows.append(doc)
        return rows
