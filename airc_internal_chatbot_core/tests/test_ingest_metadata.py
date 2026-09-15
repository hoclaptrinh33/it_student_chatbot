"""Ingest course metadata: payload fields and filename parse (no Qdrant/Docling)."""
from unittest.mock import AsyncMock

import pytest

from app.services.ingest_metadata import (
    build_qdrant_payload,
    parse_course_code_from_filename,
    resolve_ingest_metadata,
)

COURSE_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
FILE_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


def test_payload_includes_course_fields_when_provided():
    payload = build_qdrant_payload(
        chunk_id="c1",
        dataset_file_id="df1",
        dataset_id="ds1",
        is_child=True,
        parent_chunk_id=None,
        chunk_role="child",
        domain="general",
        language="vi",
        is_table=False,
        course_id=COURSE_ID,
        course_code="INT2104",
        material_type="SLIDE",
    )
    assert payload["chunk_id"] == "c1"
    assert payload["dataset_file_id"] == "df1"
    assert payload["dataset_id"] == "ds1"
    assert payload["course_id"] == COURSE_ID
    assert payload["course_code"] == "INT2104"
    assert payload["material_type"] == "SLIDE"


def test_payload_omits_course_fields_when_missing():
    payload = build_qdrant_payload(
        chunk_id="c1",
        dataset_file_id="df1",
        dataset_id="ds1",
        is_child=False,
        parent_chunk_id=None,
    )
    assert "course_id" not in payload
    assert "course_code" not in payload
    assert "material_type" not in payload


def test_parse_course_code_from_int2104_slides_filename():
    assert parse_course_code_from_filename("INT2104_slides.pdf") == "INT2104"
    assert parse_course_code_from_filename("int2104-syllabus.docx") == "INT2104"
    assert parse_course_code_from_filename("readme.pdf") is None


@pytest.mark.asyncio
async def test_resolve_prefers_explicit_then_bind_then_filename():
    course_repo = AsyncMock()
    course_repo.get_by_id_or_code = AsyncMock(
        return_value={"id": COURSE_ID, "course_code": "INT2104"}
    )
    material_repo = AsyncMock()
    material_repo.get_by_file_id = AsyncMock(return_value=None)

    explicit = await resolve_ingest_metadata(
        filename="other.pdf",
        file_id=FILE_ID,
        material_repo=material_repo,
        course_repo=course_repo,
        explicit_course_id=COURSE_ID,
        explicit_material_type="slide",
    )
    assert explicit.course_id == COURSE_ID
    assert explicit.course_code == "INT2104"
    assert explicit.material_type == "SLIDE"
    material_repo.get_by_file_id.assert_not_called()

    course_repo.get_by_id_or_code = AsyncMock(
        side_effect=lambda value: (
            {"id": COURSE_ID, "course_code": "INT2104"}
            if value in {COURSE_ID, "INT2104"}
            else None
        )
    )
    material_repo.get_by_file_id = AsyncMock(
        return_value={
            "course_id": COURSE_ID,
            "material_type": "SYLLABUS",
            "file_id": FILE_ID,
        }
    )
    bound = await resolve_ingest_metadata(
        filename="INT2104_slides.pdf",
        file_id=FILE_ID,
        material_repo=material_repo,
        course_repo=course_repo,
    )
    assert bound.course_id == COURSE_ID
    assert bound.course_code == "INT2104"
    assert bound.material_type == "SYLLABUS"

    material_repo.get_by_file_id = AsyncMock(return_value=None)
    parsed = await resolve_ingest_metadata(
        filename="INT2104_slides.pdf",
        file_id=FILE_ID,
        material_repo=material_repo,
        course_repo=course_repo,
    )
    assert parsed.course_id == COURSE_ID
    assert parsed.course_code == "INT2104"
    assert parsed.material_type == "SLIDE"
