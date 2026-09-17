"""Academic and course API permission / conflict tests (no live Postgres)."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_course_service,
    get_current_user,
    get_student_record_service,
)
from app.api.v1.academic import router as academic_router
from app.api.v1.courses import router as courses_router
from app.models.auth import User, UserRole
from app.services.course_service import CourseConflictError

SV001 = "cccccccc-cccc-cccc-cccc-cccccccccccc"
ADMIN_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

test_app = FastAPI()
test_app.include_router(courses_router, prefix="/api/v1/courses")
test_app.include_router(academic_router, prefix="/api/v1/academic")
client = TestClient(test_app)

PUT_BODY = {
    "user_id": SV001,
    "course_code": "INT1203",
    "status": "FAILED",
    "grade": 3.5,
    "semester_taken": "2024-2",
    "attempt_count": 1,
}


def _user(role: UserRole, user_id: str) -> User:
    return User(
        id=user_id,
        user_id=user_id,
        email=f"{role.value}@eaut.edu.vn",
        full_name=role.value,
        role=role,
        is_active=True,
    )


def mock_student():
    return _user(UserRole.STUDENT, SV001)


def mock_teacher():
    return _user(UserRole.TEACHER, "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def mock_admin():
    return _user(UserRole.ADMIN, ADMIN_ID)


class FakeRecordService:
    async def upsert(self, payload):
        return {
            "id": "11111111-1111-1111-1111-111111111111",
            "user_id": payload.user_id,
            "course_id": "22222222-2222-2222-2222-222222222222",
            "course_code": payload.course_code,
            "status": payload.status,
            "grade": payload.grade,
            "semester_taken": payload.semester_taken,
            "attempt_count": payload.attempt_count or 1,
        }

    async def get_transcript(self, user_id: str):
        return {"user_id": user_id, "student_code": "SV001", "full_name": "Lê Hải Đăng", "records": []}

    async def import_csv(self, raw: bytes, strict: bool = False, create_users: bool = False):
        return {
            "imported": 1,
            "errors": [{"row": 3, "reason": "unknown student_code: NOPE"}],
            "total": 2,
        }


class FakeCourseService:
    async def delete_course(self, course_id: str):
        raise CourseConflictError("Course is referenced by student_records")

    async def create_course(self, payload):
        return {
            "id": "33333333-3333-3333-3333-333333333333",
            "course_code": payload.course_code,
            "course_name": payload.course_name,
            "credits": payload.credits,
            "theory_hours": payload.theory_hours,
            "practice_hours": payload.practice_hours,
            "semester": payload.semester,
            "is_mandatory": payload.is_mandatory,
            "career_track": payload.career_track,
            "description": payload.description,
        }


def _override(user_factory, record=FakeRecordService(), course=FakeCourseService()):
    test_app.dependency_overrides[get_current_user] = user_factory
    test_app.dependency_overrides[get_student_record_service] = lambda: record
    test_app.dependency_overrides[get_course_service] = lambda: course


def test_student_cannot_put_records():
    _override(mock_student)
    try:
        response = client.put("/api/v1/academic/records", json=PUT_BODY)
        assert response.status_code == 403
    finally:
        test_app.dependency_overrides.clear()


def test_student_cannot_get_another_users_transcript():
    _override(mock_student)
    try:
        response = client.get(f"/api/v1/academic/students/{ADMIN_ID}/transcript")
        assert response.status_code == 403
    finally:
        test_app.dependency_overrides.clear()


def test_teacher_can_put_records():
    _override(mock_teacher)
    try:
        response = client.put("/api/v1/academic/records", json=PUT_BODY)
        assert response.status_code == 200
        assert response.json()["course_code"] == "INT1203"
    finally:
        test_app.dependency_overrides.clear()


def test_teacher_cannot_create_course():
    _override(mock_teacher)
    try:
        response = client.post(
            "/api/v1/courses",
            json={"course_code": "INT9999", "course_name": "Test", "credits": 3},
        )
        assert response.status_code == 403
    finally:
        test_app.dependency_overrides.clear()


def test_admin_delete_course_conflict_returns_409():
    _override(mock_admin)
    try:
        response = client.delete("/api/v1/courses/33333333-3333-3333-3333-333333333333")
        assert response.status_code == 409
        assert "student_records" in response.json()["detail"]
    finally:
        test_app.dependency_overrides.clear()


def test_csv_import_partial_when_not_strict():
    _override(mock_teacher)
    try:
        response = client.post(
            "/api/v1/academic/records/import",
            files={"file": ("grades.csv", b"student_code,course_code,status,grade,semester_taken\n", "text/csv")},
            params={"strict": "false"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["imported"] == 1
        assert body["total"] == 2
        assert len(body["errors"]) == 1
        assert body["errors"][0]["row"] == 3
    finally:
        test_app.dependency_overrides.clear()
