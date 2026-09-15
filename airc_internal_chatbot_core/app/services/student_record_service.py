"""Transcript, eligible courses, grade upsert and CSV import."""
import csv
import io
import logging
from typing import List, Optional

from app.services.cache_service import semantic_cache_service

logger = logging.getLogger(__name__)

from app.models.academic_schemas import RecordUpsert
from app.repositories.course_repository import CourseRepository
from app.repositories.prerequisite_repository import PrerequisiteRepository
from app.repositories.student_record_repository import StudentRecordRepository

CSV_BATCH_SIZE = 100
CSV_COLUMNS = ("student_code", "course_code", "status", "grade", "semester_taken")
VALID_STATUSES = {"PASSED", "FAILED", "IN_PROGRESS"}


class StudentRecordService:
    def __init__(
        self,
        record_repo: StudentRecordRepository,
        course_repo: CourseRepository,
        prerequisite_repo: Optional[PrerequisiteRepository] = None,
    ):
        self.record_repo = record_repo
        self.course_repo = course_repo
        self.prerequisite_repo = prerequisite_repo

    async def get_transcript(self, user_id: str) -> Optional[dict]:
        user = await self.record_repo.get_user(user_id)
        if not user:
            return None
        records = await self.record_repo.list_by_user(user_id)
        return {
            "user_id": user["id"],
            "student_code": user.get("student_code"),
            "full_name": user.get("full_name"),
            "records": records,
        }

    async def get_eligible_courses(self, user_id: str) -> Optional[dict]:
        user = await self.record_repo.get_user(user_id)
        if not user:
            return None
        courses = await self.record_repo.list_eligible(user_id)
        return {
            "user_id": user["id"],
            "student_code": user.get("student_code"),
            "courses": courses,
        }

    async def get_facts(self, user_id: str) -> Optional[dict]:
        transcript = await self.get_transcript(user_id)
        if not transcript:
            return None
        eligible = await self.get_eligible_courses(user_id)
        blocked = []
        if self.prerequisite_repo:
            blocked = await self.prerequisite_repo.list_blocked(user_id, limit=10)
        return {
            "student_id": transcript["user_id"],
            "student_code": transcript.get("student_code"),
            "full_name": transcript.get("full_name"),
            "records": transcript["records"],
            "eligible_courses": (eligible or {}).get("courses", []),
            "blocked_sample": blocked,
        }

    @staticmethod
    def _next_attempt(existing: Optional[dict], status: str, semester_taken: Optional[str], explicit: Optional[int]) -> int:
        if explicit is not None:
            return explicit
        if not existing:
            return 1
        if existing.get("status") == "FAILED" and (
            status != "FAILED" or semester_taken != existing.get("semester_taken")
        ):
            return int(existing.get("attempt_count") or 1) + 1
        return int(existing.get("attempt_count") or 1)

    async def upsert(self, data: RecordUpsert) -> dict:
        course = await self.course_repo.get_by_code(data.course_code)
        if not course:
            raise ValueError(f"Unknown course_code: {data.course_code}")
        user = await self.record_repo.get_user(data.user_id)
        if not user:
            raise ValueError("Unknown user_id")
        existing = await self.record_repo.get_by_user_and_course(data.user_id, course["id"])
        attempt = self._next_attempt(
            existing, data.status, data.semester_taken, data.attempt_count
        )
        result = await self.record_repo.upsert(
            user_id=data.user_id,
            course_id=course["id"],
            status=data.status,
            grade=data.grade,
            semester_taken=data.semester_taken,
            attempt_count=attempt,
        )
        self._invalidate_semantic_cache()
        return result

    async def delete_record(self, record_id: str) -> bool:
        deleted = await self.record_repo.delete(record_id)
        if deleted:
            self._invalidate_semantic_cache()
        return deleted

    @staticmethod
    def _invalidate_semantic_cache() -> None:
        semantic_cache_service.clear()
        logger.info("[GRADES] cache_invalidated_reason=grade_write")

    def _parse_csv(self, raw: bytes) -> List[dict]:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise ValueError("CSV is missing a header row")
        fields = {name.strip().lower(): name for name in reader.fieldnames if name}
        missing = [col for col in CSV_COLUMNS if col not in fields]
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(missing)}")
        rows = []
        for index, row in enumerate(reader, start=2):
            rows.append({
                "row": index,
                "student_code": (row.get(fields["student_code"]) or "").strip(),
                "course_code": (row.get(fields["course_code"]) or "").strip().upper(),
                "status": (row.get(fields["status"]) or "").strip().upper(),
                "grade": (row.get(fields["grade"]) or "").strip(),
                "semester_taken": (row.get(fields["semester_taken"]) or "").strip() or None,
            })
        return rows

    @staticmethod
    def _parse_grade(raw: str) -> Optional[float]:
        if raw is None or raw == "":
            return None
        try:
            grade = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("grade must be a number") from exc
        if grade < 0 or grade > 10:
            raise ValueError("grade must be between 0 and 10")
        return grade

    async def import_csv(
        self,
        raw: bytes,
        strict: bool = False,
        create_users: bool = False,
    ) -> dict:
        if create_users:
            raise ValueError("Creating users via CSV is not supported")
        parsed = self._parse_csv(raw)
        errors: List[dict] = []
        valid: List[tuple] = []
        for item in parsed:
            try:
                if not item["student_code"]:
                    raise ValueError("missing student_code")
                if not item["course_code"]:
                    raise ValueError("missing course_code")
                if item["status"] not in VALID_STATUSES:
                    raise ValueError(f"invalid status: {item['status'] or '(empty)'}")
                user = await self.record_repo.get_user_by_student_code(item["student_code"])
                if not user:
                    raise ValueError(f"unknown student_code: {item['student_code']}")
                course = await self.course_repo.get_by_code(item["course_code"])
                if not course:
                    raise ValueError(f"unknown course_code: {item['course_code']}")
                grade = self._parse_grade(item["grade"])
                valid.append(
                    (
                        item["row"],
                        RecordUpsert(
                            user_id=user["id"],
                            course_code=item["course_code"],
                            status=item["status"],
                            grade=grade,
                            semester_taken=item["semester_taken"],
                        ),
                    )
                )
            except ValueError as exc:
                errors.append({"row": item["row"], "reason": str(exc)})

        if strict and errors:
            return {"imported": 0, "errors": errors, "total": len(parsed)}

        imported = 0
        pending = valid
        for offset in range(0, len(pending), CSV_BATCH_SIZE):
            batch = pending[offset : offset + CSV_BATCH_SIZE]
            async with self.record_repo.session.begin_nested():
                for row_number, payload in batch:
                    try:
                        await self.upsert(payload)
                        imported += 1
                    except ValueError as exc:
                        errors.append({"row": row_number, "reason": str(exc)})
                        if strict:
                            raise
        self._invalidate_semantic_cache()
        return {"imported": imported, "errors": errors, "total": len(parsed)}
