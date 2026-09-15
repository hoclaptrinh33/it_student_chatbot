"""Course CRUD. Admin-only writes are enforced at the API layer."""
from typing import List, Optional

from app.models.academic_schemas import CourseCreate, CourseUpdate
from app.repositories.course_repository import CourseRepository
from app.repositories.prerequisite_repository import PrerequisiteRepository


class CourseConflictError(Exception):
    """Course cannot be changed because student_records still reference it."""


class CourseService:
    def __init__(
        self,
        course_repo: CourseRepository,
        prerequisite_repo: Optional[PrerequisiteRepository] = None,
    ):
        self.course_repo = course_repo
        self.prerequisite_repo = prerequisite_repo

    async def list_courses(
        self,
        semester: Optional[int] = None,
        career_track: Optional[str] = None,
        q: Optional[str] = None,
        code: Optional[str] = None,
    ) -> List[dict]:
        return await self.course_repo.list_courses(
            semester=semester,
            career_track=career_track,
            q=q,
            code=code,
        )

    async def get_course(self, course_id: str, code: Optional[str] = None) -> Optional[dict]:
        if code:
            return await self.course_repo.get_by_code(code)
        return await self.course_repo.get_by_id_or_code(course_id)

    async def create_course(self, data: CourseCreate) -> dict:
        return await self.course_repo.create_course(data.model_dump())

    async def update_course(self, course_id: str, data: CourseUpdate) -> Optional[dict]:
        existing = await self.course_repo.get_by_id_or_code(course_id)
        if not existing:
            return None
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return existing
        return await self.course_repo.update_course(existing["id"], payload)

    async def delete_course(self, course_id: str) -> bool:
        existing = await self.course_repo.get_by_id_or_code(course_id)
        if not existing:
            return False
        if await self.course_repo.count_records(existing["id"]):
            raise CourseConflictError("Course is referenced by student_records")
        return await self.course_repo.delete_course(existing["id"])
