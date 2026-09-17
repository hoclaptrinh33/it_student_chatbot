"""JWT user_id → Postgres AcademicFacts. Never trust the student utterance."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from app.services.intent_classifier import ClassifiedIntent, IntentClassifier, fold_vi

logger = logging.getLogger(__name__)

SEMESTER_RE = re.compile(r"^(\d{4})-([12])$")


def infer_next_semester(semester: str) -> Optional[str]:
    match = SEMESTER_RE.match((semester or "").strip())
    if not match:
        return None
    year, term = int(match.group(1)), match.group(2)
    if term == "2":
        return f"{year + 1}-1"
    return f"{year}-2"


def infer_current_semester(records: Sequence[dict]) -> tuple[Optional[str], str]:
    in_progress = [
        (row.get("semester_taken") or "")
        for row in records
        if row.get("status") == "IN_PROGRESS" and row.get("semester_taken")
    ]
    if in_progress:
        return max(in_progress), "IN_PROGRESS"

    completed = [
        (row.get("semester_taken") or "")
        for row in records
        if row.get("status") in {"PASSED", "FAILED"} and row.get("semester_taken")
    ]
    if completed:
        nxt = infer_next_semester(max(completed))
        if nxt:
            return nxt, "INFERRED_NEXT"

    return None, "UNKNOWN"


def _credits(row: dict) -> Optional[int]:
    value = row.get("credits")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _grade_text(row: dict) -> Optional[str]:
    grade = row.get("grade")
    if grade is None:
        return None
    try:
        return f"{float(grade):.2f}"
    except (TypeError, ValueError):
        return str(grade)


def codes_from_catalog(
    question: str,
    catalog: Sequence[dict],
    already: Optional[Sequence[str]] = None,
) -> List[str]:
    """Resolve INT#### and course-name mentions from the catalog. No per-question regex."""
    codes = [str(c).upper() for c in (already or []) if c]
    q = fold_vi(question or "")
    if not q:
        return codes
    hits: List[tuple[int, str]] = []
    for row in catalog:
        code = str(row.get("course_code") or "").upper()
        name = fold_vi(str(row.get("course_name") or ""))
        if not code:
            continue
        if re.search(rf"\b{re.escape(code.lower())}\b", q) and code not in codes:
            hits.append((1000 + len(code), code))
        elif name and len(name) >= 8 and name in q and code not in codes:
            hits.append((len(name), code))
    hits.sort(reverse=True)
    for _, code in hits:
        if code not in codes:
            codes.append(code)
    return codes


def _relation_vi(relation_type: Optional[str]) -> str:
    kind = (relation_type or "PREREQUISITE").upper()
    return {
        "PREREQUISITE": "môn tiên quyết bắt buộc",
        "PREVIOUS": "môn nên học trước",
        "CO_REQUISITE": "môn học song hành",
    }.get(kind, "môn tiên quyết bắt buộc")


def _course_label(row: dict) -> str:
    code = row.get("course_code") or ""
    name = row.get("course_name") or row.get("name") or ""
    credits = _credits(row)
    label = f"{code} {name}".strip()
    if credits is not None:
        label = f"{label} ({credits} TC)".strip()
    return label or code or "(unknown)"


@dataclass
class AcademicFacts:
    student_id: str
    student_code: Optional[str]
    full_name: str
    current_semester: Optional[str]
    current_semester_source: str
    empty_transcript: bool
    records: List[dict] = field(default_factory=list)
    eligible_courses: List[dict] = field(default_factory=list)
    blocked_sample: List[dict] = field(default_factory=list)
    career_track_filter: Optional[str] = None
    mentioned_course_codes: List[str] = field(default_factory=list)
    mentioned_prereqs: List[dict] = field(default_factory=list)
    in_progress: List[dict] = field(default_factory=list)
    retake: List[dict] = field(default_factory=list)

    @classmethod
    def empty(
        cls,
        user_id: str,
        *,
        student_code: Optional[str] = None,
        full_name: str = "",
        career_track: Optional[str] = None,
        mentioned_course_codes: Optional[List[str]] = None,
    ) -> "AcademicFacts":
        return cls(
            student_id=user_id,
            student_code=student_code,
            full_name=full_name or "",
            current_semester=None,
            current_semester_source="UNKNOWN",
            empty_transcript=True,
            career_track_filter=career_track,
            mentioned_course_codes=mentioned_course_codes or [],
        )

    def to_prompt_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "student_code": self.student_code,
            "full_name": self.full_name,
            "current_semester": self.current_semester,
            "current_semester_source": self.current_semester_source,
            "empty_transcript": self.empty_transcript,
            "records": [self._record_view(row) for row in self.records],
            "eligible_courses": [self._eligible_view(row) for row in self.eligible_courses],
            "blocked_sample": [self._blocked_view(row) for row in self.blocked_sample],
            "career_track_filter": self.career_track_filter,
            "mentioned_course_codes": list(self.mentioned_course_codes),
            "mentioned_prereqs": list(self.mentioned_prereqs),
            "in_progress": [self._record_view(row) for row in self.in_progress],
            "retake": [self._record_view(row) for row in self.retake],
        }

    def render_text(self) -> str:
        lines = ["[AcademicFacts]"]
        identity = self.full_name or "(không rõ)"
        if self.student_code:
            identity = f"{identity} ({self.student_code})"
        lines.append(f"Sinh viên: {identity}")

        if self.current_semester_source == "UNKNOWN" or not self.current_semester:
            lines.append("Học kỳ hiện tại: (không xác định — không đoán)")
        else:
            source_vi = {
                "IN_PROGRESS": "đang học",
                "INFERRED_NEXT": "suy ra từ kỳ trước",
            }.get(self.current_semester_source, "đã ghi")
            lines.append(f"Học kỳ hiện tại: {self.current_semester} ({source_vi})")

        if self.empty_transcript:
            lines.append("Bảng điểm: trống (chưa được nhập). Không suy ra môn đã đạt.")
            if self.career_track_filter:
                lines.append(f"Lọc định hướng: {self.career_track_filter}")
            return "\n".join(lines)

        if self.in_progress:
            lines.append("Đang học: " + "; ".join(_course_label(row) for row in self.in_progress))
        else:
            lines.append("Đang học: (không có)")

        passed = [row for row in self.records if row.get("status") == "PASSED"]
        if passed:
            lines.append("Đã đạt: " + "; ".join(_course_label(row) for row in passed))
        else:
            lines.append("Đã đạt: (không có)")

        if self.retake:
            parts = []
            for row in self.retake:
                extra = []
                grade = _grade_text(row)
                if grade:
                    extra.append(grade)
                if row.get("semester_taken"):
                    extra.append(str(row["semester_taken"]))
                suffix = f" ({', '.join(extra)})" if extra else ""
                parts.append(_course_label(row) + suffix)
            lines.append("Chưa đạt, cần học lại: " + "; ".join(parts))
        else:
            lines.append("Chưa đạt, cần học lại: (không có)")

        if self.eligible_courses:
            parts = []
            for row in self.eligible_courses:
                label = _course_label(row)
                notes = []
                if row.get("course_code") in {r.get("course_code") for r in self.retake}:
                    notes.append("học lại")
                previous = row.get("recommended_previous") or []
                if previous:
                    notes.append("nên học trước nhưng chưa đạt: " + ", ".join(previous))
                if notes:
                    credits = _credits(row)
                    core = row.get("course_code") or ""
                    if credits is not None:
                        label = f"{core} ({credits} TC, {'; '.join(notes)})"
                        name = row.get("course_name")
                        if name:
                            label = f"{core} {name} ({credits} TC, {'; '.join(notes)})"
                    else:
                        label = f"{label} ({'; '.join(notes)})"
                parts.append(label)
            lines.append("Môn đủ điều kiện: " + "; ".join(parts))
        else:
            lines.append("Môn đủ điều kiện: (không có)")

        if self.career_track_filter:
            lines.append(f"Lọc định hướng: {self.career_track_filter}")

        track = self.career_track_filter
        track_blocked = [
            row for row in self.blocked_sample if track and row.get("career_track") == track
        ]
        other_blocked = [
            row for row in self.blocked_sample if not track or row.get("career_track") != track
        ]
        if track:
            if track_blocked:
                lines.append(
                    f"Môn {track} bị chặn: " + "; ".join(self._blocked_label(row) for row in track_blocked)
                )
            else:
                lines.append(f"Môn {track} bị chặn: (không có)")
        if other_blocked:
            prefix = "Môn cứng bị chặn (ngoài WEB): " if track == "WEB" else "Môn cứng bị chặn: "
            lines.append(prefix + "; ".join(self._blocked_label(row) for row in other_blocked))

        if self.mentioned_prereqs:
            grouped: Dict[str, List[str]] = {}
            for row in self.mentioned_prereqs:
                code = row.get("course_code") or ""
                grouped.setdefault(code, []).append(
                    f"{row.get('prerequisite_code')} ({_relation_vi(row.get('relation_type'))}, bậc {row.get('depth')})"
                )
            for code, items in grouped.items():
                lines.append(f"Tiên quyết của {code}: " + "; ".join(items))

        return "\n".join(lines)

    @staticmethod
    def _record_view(row: dict) -> dict:
        return {
            "course_code": row.get("course_code"),
            "name": row.get("course_name") or row.get("name"),
            "credits": _credits(row),
            "status": row.get("status"),
            "grade": row.get("grade"),
            "semester_taken": row.get("semester_taken"),
            "attempt_count": row.get("attempt_count"),
            "career_track": row.get("career_track"),
        }

    @staticmethod
    def _eligible_view(row: dict) -> dict:
        return {
            "course_code": row.get("course_code"),
            "name": row.get("course_name") or row.get("name"),
            "credits": _credits(row),
            "career_track": row.get("career_track"),
            "missing_prereq_codes": list(row.get("missing_prereq_codes") or []),
            "recommended_previous": list(row.get("recommended_previous") or []),
            "relation_type": list(row.get("relation_type") or []),
        }

    @staticmethod
    def _blocked_view(row: dict) -> dict:
        return {
            "course_code": row.get("course_code"),
            "name": row.get("course_name") or row.get("name"),
            "credits": _credits(row),
            "career_track": row.get("career_track"),
            "missing_prereq_codes": list(row.get("missing_prereq_codes") or []),
            "relation_type": row.get("relation_type") or "PREREQUISITE",
        }

    @staticmethod
    def _blocked_label(row: dict) -> str:
        missing = ", ".join(row.get("missing_prereq_codes") or [])
        rel = _relation_vi(row.get("relation_type"))
        reason = f"chưa đạt {rel}: {missing}" if missing else f"chưa đạt {rel}"
        return f"{_course_label(row)}, {reason}"


class AcademicFactsService:
    def __init__(self, record_repo, course_repo=None, prerequisite_repo=None):
        self.record_repo = record_repo
        self.course_repo = course_repo
        self.prerequisite_repo = prerequisite_repo
        self._classifier = IntentClassifier()

    async def build(
        self,
        user_id: str,
        question: str = "",
        classified: Optional[ClassifiedIntent] = None,
    ) -> AcademicFacts:
        classified = classified or self._classifier.classify(question)
        user = await self.record_repo.get_user(user_id)
        if not user:
            mentioned = await self._mentioned_codes(question, classified)
            return AcademicFacts.empty(
                user_id,
                career_track=classified.career_track,
                mentioned_course_codes=mentioned,
            )

        records = await self.record_repo.list_by_user(user_id)
        full_name = user.get("full_name") or ""
        student_code = user.get("student_code")
        if not records:
            logger.info("[FACTS] empty_transcript user=%s", user_id)
            facts = AcademicFacts.empty(
                user_id,
                student_code=student_code,
                full_name=full_name,
                career_track=classified.career_track,
                mentioned_course_codes=list(classified.course_codes),
            )
            facts.mentioned_course_codes = await self._mentioned_codes(question, classified)
            facts.mentioned_prereqs = await self._closures(facts.mentioned_course_codes)
            return facts

        current_semester, source = infer_current_semester(records)
        in_progress = [row for row in records if row.get("status") == "IN_PROGRESS"]
        retake = [row for row in records if row.get("status") == "FAILED"]
        eligible = await self.record_repo.list_eligible(user_id)
        blocked = []
        if self.prerequisite_repo:
            blocked = await self.prerequisite_repo.list_blocked(user_id, limit=30)

        mentioned = await self._mentioned_codes(question, classified)
        closures = await self._closures(mentioned)

        logger.info(
            "[FACTS] user=%s eligible=%s blocked=%s semester=%s source=%s",
            user_id,
            len(eligible),
            len(blocked),
            current_semester,
            source,
        )
        return AcademicFacts(
            student_id=str(user.get("id") or user_id),
            student_code=student_code,
            full_name=full_name,
            current_semester=current_semester,
            current_semester_source=source,
            empty_transcript=False,
            records=records,
            eligible_courses=eligible,
            blocked_sample=blocked,
            career_track_filter=classified.career_track,
            mentioned_course_codes=mentioned,
            mentioned_prereqs=closures,
            in_progress=in_progress,
            retake=retake,
        )

    async def _mentioned_codes(self, question: str, classified: ClassifiedIntent) -> List[str]:
        already = list(classified.course_codes)
        if not self.course_repo:
            return already
        try:
            catalog = await self.course_repo.list_courses()
        except Exception as exc:
            logger.info("[FACTS] catalog lookup skipped: %s", exc)
            return already
        return codes_from_catalog(question, catalog, already)

    async def _closures(self, course_codes: Sequence[str]) -> List[dict]:
        if not course_codes or not self.prerequisite_repo:
            return []
        out: List[dict] = []
        for code in course_codes:
            rows = await self.prerequisite_repo.list_closure_by_code(code)
            for row in rows:
                item = dict(row)
                item.setdefault("course_code", code.upper())
                out.append(item)
        return out
