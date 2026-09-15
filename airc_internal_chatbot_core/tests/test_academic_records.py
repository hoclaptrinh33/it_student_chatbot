"""StudentRecordService upsert + CSV import unit tests."""
from unittest.mock import AsyncMock, MagicMock

import pytest

import numpy as np

from app.models.academic_schemas import RecordUpsert
from app.services.cache_service import semantic_cache_service
from app.services.student_record_service import StudentRecordService

SV001 = "cccccccc-cccc-cccc-cccc-cccccccccccc"
COURSE_ID = "44444444-4444-4444-4444-444444444444"


class _Nested:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_upsert_increments_attempt_when_failed_reregistered():
    record_repo = AsyncMock()
    record_repo.session = MagicMock(begin_nested=MagicMock(return_value=_Nested()))
    record_repo.get_user = AsyncMock(return_value={"id": SV001, "student_code": "SV001"})
    record_repo.get_by_user_and_course = AsyncMock(
        return_value={"id": "r1", "status": "FAILED", "attempt_count": 1, "semester_taken": "2024-2"}
    )
    record_repo.upsert = AsyncMock(
        return_value={"id": "r1", "user_id": SV001, "course_id": COURSE_ID, "attempt_count": 2, "status": "IN_PROGRESS"}
    )
    course_repo = AsyncMock()
    course_repo.get_by_code = AsyncMock(
        return_value={"id": COURSE_ID, "course_code": "INT1203"}
    )
    service = StudentRecordService(record_repo, course_repo)

    await service.upsert(
        RecordUpsert(
            user_id=SV001,
            course_code="INT1203",
            status="IN_PROGRESS",
            semester_taken="2025-1",
        )
    )
    kwargs = record_repo.upsert.await_args.kwargs
    assert kwargs["attempt_count"] == 2


@pytest.mark.asyncio
async def test_grade_upsert_clears_semantic_cache():
    semantic_cache_service.clear()
    vec = np.ones(8, dtype=float)
    semantic_cache_service.set(
        "hybrid question",
        vec,
        "cached answer for SV001",
        suffix="_bot_x_user_cccccccc",
    )
    assert semantic_cache_service.get("hybrid question", vec, suffix="_bot_x_user_cccccccc")

    record_repo = AsyncMock()
    record_repo.get_user = AsyncMock(return_value={"id": SV001, "student_code": "SV001"})
    record_repo.get_by_user_and_course = AsyncMock(return_value=None)
    record_repo.upsert = AsyncMock(
        return_value={"id": "r1", "user_id": SV001, "course_id": COURSE_ID, "status": "PASSED"}
    )
    course_repo = AsyncMock()
    course_repo.get_by_code = AsyncMock(return_value={"id": COURSE_ID, "course_code": "INT1203"})
    service = StudentRecordService(record_repo, course_repo)

    await service.upsert(
        RecordUpsert(user_id=SV001, course_code="INT1203", status="PASSED", grade=7.0, semester_taken="2025-1")
    )
    assert semantic_cache_service.get("hybrid question", vec, suffix="_bot_x_user_cccccccc") is None


@pytest.mark.asyncio
async def test_csv_import_partial_results_when_not_strict():
    record_repo = AsyncMock()
    record_repo.session = MagicMock(begin_nested=MagicMock(return_value=_Nested()))
    record_repo.get_user_by_student_code = AsyncMock(
        side_effect=lambda code: {"id": SV001, "student_code": "SV001"} if code == "SV001" else None
    )
    record_repo.get_user = AsyncMock(return_value={"id": SV001, "student_code": "SV001"})
    record_repo.get_by_user_and_course = AsyncMock(return_value=None)
    record_repo.upsert = AsyncMock(
        return_value={
            "id": "r1",
            "user_id": SV001,
            "course_id": COURSE_ID,
            "course_code": "INT1101",
            "status": "PASSED",
            "grade": 8.0,
            "attempt_count": 1,
        }
    )
    course_repo = AsyncMock()
    course_repo.get_by_code = AsyncMock(
        side_effect=lambda code: {"id": COURSE_ID, "course_code": code} if code == "INT1101" else None
    )
    service = StudentRecordService(record_repo, course_repo)

    csv_body = (
        "student_code,course_code,status,grade,semester_taken\n"
        "SV001,INT1101,PASSED,8.0,2024-1\n"
        "NOPE,INT1101,PASSED,7.0,2024-1\n"
    ).encode("utf-8")

    result = await service.import_csv(csv_body, strict=False)
    assert result["imported"] == 1
    assert result["total"] == 2
    assert len(result["errors"]) == 1
    assert result["errors"][0]["row"] == 3
    assert "unknown student_code" in result["errors"][0]["reason"]


@pytest.mark.asyncio
async def test_delete_course_conflicts_when_records_exist():
    from app.services.course_service import CourseConflictError, CourseService

    course_repo = AsyncMock()
    course_repo.get_by_id_or_code = AsyncMock(
        return_value={"id": COURSE_ID, "course_code": "INT1101"}
    )
    course_repo.count_records = AsyncMock(return_value=1)
    service = CourseService(course_repo)
    with pytest.raises(CourseConflictError):
        await service.delete_course(COURSE_ID)
    course_repo.delete_course.assert_not_called()
