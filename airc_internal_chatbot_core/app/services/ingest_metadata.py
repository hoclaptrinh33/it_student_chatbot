"""Resolve course_id / course_code / material_type for ingest payloads."""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)

COURSE_CODE_RE = re.compile(r"([A-Za-z]{2,4}\d{4})")


@dataclass
class IngestCourseMetadata:
    course_id: Optional[str] = None
    course_code: Optional[str] = None
    material_type: Optional[str] = None


def parse_course_code_from_filename(filename: str) -> Optional[str]:
    if not filename:
        return None
    match = COURSE_CODE_RE.search(os.path.basename(filename))
    return match.group(1).upper() if match else None


def infer_material_type_from_filename(filename: str) -> Optional[str]:
    if not filename:
        return None
    lower = filename.lower()
    if any(token in lower for token in ("slide", "bai giang", "bài giảng")):
        return "SLIDE"
    if any(token in lower for token in ("syllabus", "de cuong", "đề cương")):
        return "SYLLABUS"
    if any(token in lower for token in ("exam", "de thi", "đề thi")):
        return "EXAM"
    if any(token in lower for token in ("textbook", "giao trinh", "giáo trình")):
        return "TEXTBOOK"
    return None


def build_qdrant_payload(
    *,
    chunk_id: str,
    dataset_file_id: str,
    dataset_id: str,
    is_child: bool,
    parent_chunk_id: Optional[str],
    chunk_role: str = "standalone",
    domain: str = "general",
    language: str = "vi",
    is_table: bool = False,
    course_id: Optional[str] = None,
    course_code: Optional[str] = None,
    material_type: Optional[str] = None,
) -> dict:
    payload = {
        "chunk_id": str(chunk_id),
        "dataset_file_id": dataset_file_id,
        "dataset_id": dataset_id,
        "is_child": is_child,
        "parent_chunk_id": parent_chunk_id,
        "chunk_role": chunk_role,
        "domain": domain,
        "language": language,
        "is_table": is_table,
    }
    if course_id:
        payload["course_id"] = str(course_id)
    if course_code:
        payload["course_code"] = str(course_code).strip().upper()
    if material_type:
        payload["material_type"] = str(material_type).strip().upper()
    return payload


async def _lookup_course(course_repo: Any, value: str) -> Optional[dict]:
    if not course_repo or not value:
        return None
    getter = getattr(course_repo, "get_by_id_or_code", None)
    if getter:
        return await getter(value)
    by_id = getattr(course_repo, "get_by_id", None)
    if by_id:
        found = await by_id(value)
        if found:
            return found
    by_code = getattr(course_repo, "get_by_code", None)
    if by_code:
        return await by_code(value)
    return None


def _apply_course(meta: IngestCourseMetadata, course: dict, fallback_id: Optional[str] = None) -> None:
    meta.course_id = str(course.get("id") or fallback_id or "") or None
    code = course.get("course_code")
    if code:
        meta.course_code = str(code).strip().upper()


async def resolve_ingest_metadata(
    filename: str,
    file_id: Optional[str] = None,
    material_repo: Any = None,
    course_repo: Any = None,
    explicit_course_id: Optional[str] = None,
    explicit_material_type: Optional[str] = None,
) -> IngestCourseMetadata:
    """Prefer upload form fields, then learning_materials bind, then filename."""
    meta = IngestCourseMetadata()
    if explicit_material_type and str(explicit_material_type).strip():
        meta.material_type = str(explicit_material_type).strip().upper()

    if explicit_course_id and str(explicit_course_id).strip():
        raw = str(explicit_course_id).strip()
        course = await _lookup_course(course_repo, raw)
        if course:
            _apply_course(meta, course, raw)
        else:
            meta.course_id = raw
            parsed = parse_course_code_from_filename(raw)
            if parsed:
                meta.course_code = parsed

    if (not meta.course_id or not meta.material_type or not meta.course_code) and material_repo and file_id:
        getter = getattr(material_repo, "get_by_file_id", None)
        material = await getter(file_id) if getter else None
        if material:
            if not meta.course_id and material.get("course_id"):
                meta.course_id = str(material["course_id"])
            if not meta.material_type and material.get("material_type"):
                meta.material_type = str(material["material_type"]).strip().upper()
            if meta.course_id and not meta.course_code:
                course = await _lookup_course(course_repo, meta.course_id)
                if course:
                    _apply_course(meta, course, meta.course_id)

    if not meta.course_code:
        parsed = parse_course_code_from_filename(filename)
        if parsed:
            logger.warning(
                "[INGEST] Parsed course code %s from filename %s (no upload/bind metadata)",
                parsed,
                filename,
            )
            meta.course_code = parsed
            if not meta.course_id:
                course = await _lookup_course(course_repo, parsed)
                if course:
                    _apply_course(meta, course, parsed)

    if not meta.material_type:
        meta.material_type = infer_material_type_from_filename(filename)
    return meta
