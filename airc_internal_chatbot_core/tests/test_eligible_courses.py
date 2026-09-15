"""Eligible courses for SV001 via fn_student_eligible_courses (live Postgres if up)."""
import os
from unittest.mock import AsyncMock

import pytest

from app.services.student_record_service import StudentRecordService

SV001 = "cccccccc-cccc-cccc-cccc-cccccccccccc"
EXPECTED = {"INT1203", "INT2102", "INT2202"}


@pytest.mark.asyncio
async def test_sv001_eligible_codes_from_sql_function():
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot",
    )
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT course_code FROM fn_student_eligible_courses(:uid) "
                    "ORDER BY course_code"
                ),
                {"uid": SV001},
            )
            codes = {row[0] for row in result}
    except Exception as exc:
        pytest.skip(f"it_postgres unavailable: {exc}")
    finally:
        await engine.dispose()

    assert codes == EXPECTED


@pytest.mark.asyncio
async def test_service_eligible_courses_passthrough():
    record_repo = AsyncMock()
    record_repo.get_user = AsyncMock(
        return_value={"id": SV001, "student_code": "SV001", "full_name": "Lê Hải Đăng"}
    )
    record_repo.list_eligible = AsyncMock(
        return_value=[
            {"course_id": "1", "course_code": "INT1203", "course_name": "Kiến trúc máy tính"},
            {"course_id": "2", "course_code": "INT2102", "course_name": "Mạng máy tính"},
            {"course_id": "3", "course_code": "INT2202", "course_name": "Trí tuệ nhân tạo"},
        ]
    )
    service = StudentRecordService(record_repo, AsyncMock())
    data = await service.get_eligible_courses(SV001)
    assert {c["course_code"] for c in data["courses"]} == EXPECTED
