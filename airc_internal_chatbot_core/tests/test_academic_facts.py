"""AcademicFactsService unit + optional live SV001 checks."""
import os
from unittest.mock import AsyncMock

import pytest

from app.services.academic_facts_service import (
    AcademicFactsService,
    codes_from_catalog,
    infer_current_semester,
)
from app.services.intent_classifier import IntentClassifier

SV001 = "cccccccc-cccc-cccc-cccc-cccccccccccc"

SV001_RECORDS = [
    {"course_code": "INT1101", "course_name": "Nhập môn lập trình", "credits": 3, "status": "PASSED", "grade": 8.50, "semester_taken": "2024-1"},
    {"course_code": "INT1102", "course_name": "Toán rời rạc", "credits": 3, "status": "PASSED", "grade": 7.00, "semester_taken": "2024-1"},
    {"course_code": "INT1103", "course_name": "Đại số tuyến tính", "credits": 3, "status": "PASSED", "grade": 6.50, "semester_taken": "2024-1"},
    {"course_code": "INT1104", "course_name": "Nhập môn CNTT", "credits": 2, "status": "PASSED", "grade": 9.00, "semester_taken": "2024-1"},
    {"course_code": "INT1201", "course_name": "CTDL & GT", "credits": 4, "status": "PASSED", "grade": 7.50, "semester_taken": "2024-2"},
    {"course_code": "INT1202", "course_name": "Cơ sở dữ liệu", "credits": 3, "status": "PASSED", "grade": 8.00, "semester_taken": "2024-2"},
    {"course_code": "INT1203", "course_name": "Kiến trúc máy tính", "credits": 3, "status": "FAILED", "grade": 3.50, "semester_taken": "2024-2"},
    {"course_code": "INT1204", "course_name": "OOP", "credits": 3, "status": "PASSED", "grade": 8.00, "semester_taken": "2024-2"},
    {"course_code": "INT2103", "course_name": "Phân tích và thiết kế hệ thống", "credits": 3, "status": "IN_PROGRESS", "grade": None, "semester_taken": "2025-1"},
    {"course_code": "INT2104", "course_name": "Lập trình Web", "credits": 3, "status": "IN_PROGRESS", "grade": None, "semester_taken": "2025-1"},
]

SV001_ELIGIBLE = [
    {"course_code": "INT1203", "course_name": "Kiến trúc máy tính", "credits": 3, "recommended_previous": []},
    {"course_code": "INT2102", "course_name": "Mạng máy tính", "credits": 3, "recommended_previous": ["INT1203"]},
    {"course_code": "INT2202", "course_name": "Trí tuệ nhân tạo", "credits": 3, "recommended_previous": []},
]

SV001_BLOCKED = [
    {
        "course_code": "INT2204",
        "course_name": "Phát triển ứng dụng Web",
        "credits": 3,
        "career_track": "WEB",
        "missing_prereq_codes": ["INT2104"],
        "relation_type": "PREREQUISITE",
    },
    {
        "course_code": "INT2101",
        "course_name": "Hệ điều hành",
        "credits": 3,
        "career_track": "GENERAL",
        "missing_prereq_codes": ["INT1203"],
        "relation_type": "PREREQUISITE",
    },
]


def _service(records=None, user=None, eligible=None, blocked=None):
    record_repo = AsyncMock()
    record_repo.get_user = AsyncMock(
        return_value=user if user is not None else {
            "id": SV001,
            "student_code": "SV001",
            "full_name": "Lê Hải Đăng",
            "role": "student",
        }
    )
    record_repo.list_by_user = AsyncMock(return_value=list(records if records is not None else SV001_RECORDS))
    record_repo.list_eligible = AsyncMock(return_value=list(eligible if eligible is not None else SV001_ELIGIBLE))
    prereq_repo = AsyncMock()
    prereq_repo.list_blocked = AsyncMock(return_value=list(blocked if blocked is not None else SV001_BLOCKED))
    prereq_repo.list_closure_by_code = AsyncMock(return_value=[])
    return AcademicFactsService(record_repo, AsyncMock(), prereq_repo)


def test_infer_semester_prefers_in_progress():
    semester, source = infer_current_semester(SV001_RECORDS)
    assert semester == "2025-1"
    assert source == "IN_PROGRESS"


def test_infer_semester_unknown_when_empty():
    semester, source = infer_current_semester([])
    assert semester is None
    assert source == "UNKNOWN"


@pytest.mark.asyncio
async def test_empty_transcript_flag():
    service = _service(records=[], user={"id": "new", "student_code": "SVNEW", "full_name": "Tân sinh viên"})
    facts = await service.build("new", "em nên học môn nào")
    assert facts.empty_transcript is True
    assert facts.eligible_courses == []
    assert facts.current_semester_source == "UNKNOWN"


@pytest.mark.asyncio
async def test_utterance_passed_int1203_still_failed_from_records():
    service = _service()
    facts = await service.build(SV001, "em đã qua INT1203 rồi cô ơi")
    statuses = {row["course_code"]: row["status"] for row in facts.records}
    assert statuses["INT1203"] == "FAILED"
    assert any(row["course_code"] == "INT1203" for row in facts.retake)
    prompt = facts.render_text()
    assert "INT1203" in prompt
    assert "Chưa đạt, cần học lại" in prompt
    passed_line = next(line for line in prompt.splitlines() if line.startswith("Đã đạt:"))
    assert "INT1203" not in passed_line


@pytest.mark.asyncio
async def test_sv001_web_facts():
    classified = IntentClassifier().classify(
        "E muốn theo đường dev web thì học kì này lên học những môn nào"
    )
    service = _service()
    facts = await service.build(SV001, classified=classified, question="web")
    assert facts.current_semester == "2025-1"
    assert facts.current_semester_source == "IN_PROGRESS"
    assert {row["course_code"] for row in facts.in_progress} == {"INT2103", "INT2104"}
    assert any(row["course_code"] == "INT1203" and row["status"] == "FAILED" for row in facts.records)
    eligible_codes = {row["course_code"] for row in facts.eligible_courses}
    assert {"INT1203", "INT2102", "INT2202"} <= eligible_codes
    blocked_web = [row for row in facts.blocked_sample if row["course_code"] == "INT2204"]
    assert blocked_web
    assert "INT2104" in blocked_web[0]["missing_prereq_codes"]
    assert facts.career_track_filter == "WEB"


@pytest.mark.asyncio
async def test_sv001_web_facts_live_postgres():
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.repositories.course_repository import CourseRepository
    from app.repositories.prerequisite_repository import PrerequisiteRepository
    from app.repositories.student_record_repository import StudentRecordRepository

    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot",
    )
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with SessionLocal() as session:
            service = AcademicFactsService(
                StudentRecordRepository(session),
                CourseRepository(session),
                PrerequisiteRepository(session),
            )
            facts = await service.build(
                SV001,
                "E muốn theo đường dev web thì học kì này lên học những môn nào",
            )
    except Exception as exc:
        pytest.skip(f"it_postgres unavailable: {exc}")
    finally:
        await engine.dispose()

    assert facts.current_semester == "2025-1"
    assert {row["course_code"] for row in facts.in_progress} == {"INT2103", "INT2104"}
    assert any(row["course_code"] == "INT1203" and row["status"] == "FAILED" for row in facts.records)
    eligible_codes = {row["course_code"] for row in facts.eligible_courses}
    assert {"INT1203", "INT2102", "INT2202"} <= eligible_codes
    blocked = next(row for row in facts.blocked_sample if row["course_code"] == "INT2204")
    assert "INT2104" in (blocked.get("missing_prereq_codes") or [])
    assert facts.career_track_filter == "WEB"


def test_codes_from_catalog_matches_vietnamese_course_name():
    catalog = [
        {"course_code": "INT1201", "course_name": "Cấu trúc dữ liệu và giải thuật"},
        {"course_code": "INT2104", "course_name": "Lập trình Web"},
    ]
    codes = codes_from_catalog(
        "Tìm cho t tài liệu của môn cấu trúc dữ liệu và giải thuật",
        catalog,
    )
    assert codes == ["INT1201"]
