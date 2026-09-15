"""Prerequisite graph + why a course is blocked."""
from typing import List, Optional

from app.models.academic_schemas import PrerequisiteCreate
from app.repositories.course_repository import CourseRepository
from app.repositories.prerequisite_repository import PrerequisiteRepository


class PrerequisiteService:
    def __init__(
        self,
        prerequisite_repo: PrerequisiteRepository,
        course_repo: CourseRepository,
    ):
        self.prerequisite_repo = prerequisite_repo
        self.course_repo = course_repo

    async def get_course_prerequisites(self, course_id: str) -> Optional[dict]:
        course = await self.course_repo.get_by_id_or_code(course_id)
        if not course:
            return None
        direct = await self.prerequisite_repo.list_direct(course["id"])
        closure = await self.prerequisite_repo.list_closure(course["id"])
        hard = [edge for edge in direct if edge.get("relation_type") == "PREREQUISITE"]
        soft = [edge for edge in direct if edge.get("relation_type") in ("PREVIOUS", "CO_REQUISITE")]
        return {
            "course_id": course["id"],
            "course_code": course["course_code"],
            "course_name": course["course_name"],
            "hard": hard,
            "soft": soft,
            "closure": closure,
        }

    def explain_blocked(self, course: dict, missing: List[str], recommended: List[str]) -> str:
        code = course.get("course_code", "")
        name = course.get("course_name", "")
        label = f"{code} {name}".strip()
        if missing:
            joined = ", ".join(missing)
            return f"Chưa học được {label} vì chưa PASSED tiên quyết cứng: {joined}."
        if recommended:
            joined = ", ".join(recommended)
            return f"{label} được đăng ký; khuyến nghị hoàn thành môn trước (PREVIOUS): {joined}."
        return f"{label} đủ điều kiện đăng ký."

    async def add_prerequisite(self, course_id: str, data: PrerequisiteCreate) -> dict:
        course = await self.course_repo.get_by_id_or_code(course_id)
        if not course:
            raise KeyError("Course not found")
        prereq = await self.course_repo.get_by_id_or_code(data.prerequisite_course_id)
        if not prereq:
            raise ValueError("Prerequisite course not found")
        return await self.prerequisite_repo.add_edge(
            course["id"],
            prereq["id"],
            data.relation_type,
        )

    async def delete_prerequisite(self, course_id: str, prereq_id: str) -> bool:
        course = await self.course_repo.get_by_id_or_code(course_id)
        if not course:
            return False
        deleted = await self.prerequisite_repo.delete_edge(course["id"], prereq_id)
        return deleted > 0
