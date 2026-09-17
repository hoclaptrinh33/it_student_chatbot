"""Bind learning_materials writes file_id + course_id + material_type."""
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user, get_learning_material_service
from app.api.v1.academic import router as academic_router
from app.models.academic_schemas import MaterialCreate
from app.models.auth import User, UserRole
from app.services.learning_material_service import LearningMaterialService

COURSE_ID = "22222222-2222-2222-2222-222222222222"
FILE_ID = "44444444-4444-4444-4444-444444444444"
DATASET_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"


@pytest.mark.asyncio
async def test_bind_material_writes_file_id_course_id_material_type():
    material_repo = AsyncMock()
    material_repo.create_material = AsyncMock(
        return_value={
            "id": "55555555-5555-5555-5555-555555555555",
            "course_id": COURSE_ID,
            "title": "INT2104_slides.pdf",
            "material_type": "SLIDE",
            "file_id": FILE_ID,
            "dataset_id": DATASET_ID,
            "file_url": "uploads/INT2104_slides.pdf",
        }
    )
    course_repo = AsyncMock()
    course_repo.get_by_id_or_code = AsyncMock(
        return_value={"id": COURSE_ID, "course_code": "INT2104"}
    )
    file_repo = AsyncMock()
    file_repo.get_by_id = AsyncMock(
        return_value={
            "id": FILE_ID,
            "name": "INT2104_slides.pdf",
            "path": "uploads/INT2104_slides.pdf",
        }
    )

    service = LearningMaterialService(material_repo, course_repo, file_repo)
    result = await service.bind_material(
        MaterialCreate(
            course_id=COURSE_ID,
            file_id=FILE_ID,
            material_type="slide",
            dataset_id=DATASET_ID,
        )
    )

    created = material_repo.create_material.call_args[0][0]
    assert created["file_id"] == FILE_ID
    assert created["course_id"] == COURSE_ID
    assert created["material_type"] == "SLIDE"
    assert created["dataset_id"] == DATASET_ID
    assert created["title"] == "INT2104_slides.pdf"
    assert result["file_id"] == FILE_ID
    assert result["course_id"] == COURSE_ID
    assert result["material_type"] == "SLIDE"


def test_bind_material_api_persists_file_and_course_fields():
    app = FastAPI()
    app.include_router(academic_router, prefix="/api/v1/academic")
    captured = {}

    class FakeMaterialService:
        async def bind_material(self, payload: MaterialCreate):
            captured["payload"] = payload
            return {
                "id": "55555555-5555-5555-5555-555555555555",
                "course_id": payload.course_id,
                "title": payload.title or "INT2104_slides.pdf",
                "material_type": payload.material_type,
                "file_id": payload.file_id,
                "dataset_id": payload.dataset_id,
                "file_url": payload.file_url,
            }

    app.dependency_overrides[get_current_user] = lambda: User(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        user_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        email="teacher@eau.edu.vn",
        full_name="teacher",
        role=UserRole.TEACHER,
        is_active=True,
    )
    app.dependency_overrides[get_learning_material_service] = lambda: FakeMaterialService()
    client = TestClient(app)
    try:
        response = client.post(
            "/api/v1/academic/materials",
            json={
                "course_id": COURSE_ID,
                "file_id": FILE_ID,
                "material_type": "SLIDE",
                "dataset_id": DATASET_ID,
                "title": "INT2104_slides.pdf",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["file_id"] == FILE_ID
        assert body["course_id"] == COURSE_ID
        assert body["material_type"] == "SLIDE"
        assert body["dataset_id"] == DATASET_ID
        assert captured["payload"].file_id == FILE_ID
        assert captured["payload"].course_id == COURSE_ID
        assert captured["payload"].material_type == "SLIDE"
    finally:
        app.dependency_overrides.clear()


def test_delete_material_api_success():
    app = FastAPI()
    app.include_router(academic_router, prefix="/api/v1/academic")

    class FakeMaterialService:
        async def delete_material(self, material_id: str):
            return material_id == "55555555-5555-5555-5555-555555555555"

    app.dependency_overrides[get_current_user] = lambda: User(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        user_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        email="teacher@eau.edu.vn",
        full_name="teacher",
        role=UserRole.TEACHER,
        is_active=True,
    )
    app.dependency_overrides[get_learning_material_service] = lambda: FakeMaterialService()
    client = TestClient(app)
    try:
        resp = client.delete("/api/v1/academic/materials/55555555-5555-5555-5555-555555555555")
        assert resp.status_code == 204

        resp_not_found = client.delete("/api/v1/academic/materials/00000000-0000-0000-0000-000000000000")
        assert resp_not_found.status_code == 404
    finally:
        app.dependency_overrides.clear()
