"""List/bind learning materials to uploaded files."""
from typing import List, Optional

from app.models.academic_schemas import MaterialCreate, MaterialUpdate
from app.repositories.course_repository import CourseRepository
from app.repositories.file_repository import FileRepository
from app.repositories.learning_material_repository import LearningMaterialRepository


class LearningMaterialService:
    def __init__(
        self,
        material_repo: LearningMaterialRepository,
        course_repo: CourseRepository,
        file_repo: Optional[FileRepository] = None,
    ):
        self.material_repo = material_repo
        self.course_repo = course_repo
        self.file_repo = file_repo

    async def list_materials(
        self,
        course_id: Optional[str] = None,
        material_type: Optional[str] = None,
    ) -> List[dict]:
        return await self.material_repo.list_materials(course_id=course_id, material_type=material_type)

    async def bind_material(self, data: MaterialCreate) -> dict:
        course = await self.course_repo.get_by_id_or_code(data.course_id)
        if not course:
            raise ValueError("Course not found")
        title = data.title
        file_url = data.file_url
        if data.file_id:
            if not self.file_repo:
                raise ValueError("File repository is not configured")
            file_doc = await self.file_repo.get_by_id(data.file_id)
            if not file_doc:
                raise ValueError("file_id not found")
            title = title or file_doc.get("name") or "Untitled material"
            file_url = file_url or file_doc.get("path")
        if not title:
            raise ValueError("title is required when file_id is omitted")
        return await self.material_repo.create_material({
            "course_id": course["id"],
            "title": title,
            "material_type": data.material_type,
            "file_url": file_url,
            "file_id": data.file_id,
            "dataset_id": data.dataset_id,
        })

    async def update_material(self, material_id: str, data: MaterialUpdate) -> Optional[dict]:
        existing = await self.material_repo.get_by_id(material_id)
        if not existing:
            return None
        payload = data.model_dump(exclude_unset=True)
        if "course_id" in payload and payload["course_id"]:
            course = await self.course_repo.get_by_id_or_code(payload["course_id"])
            if not course:
                raise ValueError("Course not found")
            payload["course_id"] = course["id"]
        return await self.material_repo.update_material(material_id, payload)
