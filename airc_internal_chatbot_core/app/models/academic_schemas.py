"""Pydantic schemas for academic course / record / material APIs."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


CAREER_TRACKS = ("GENERAL", "AI", "WEB", "SECURITY", "DATA", "NETWORK", "SOFTWARE")
RECORD_STATUSES = ("PASSED", "FAILED", "IN_PROGRESS")
RELATION_TYPES = ("PREREQUISITE", "PREVIOUS", "CO_REQUISITE")
MATERIAL_TYPES = ("SYLLABUS", "SLIDE", "TEXTBOOK", "EXAM")


class CourseCreate(BaseModel):
    course_code: str = Field(..., min_length=2, max_length=20)
    course_name: str = Field(..., min_length=1, max_length=255)
    credits: int = Field(..., gt=0)
    theory_hours: int = Field(default=0, ge=0)
    practice_hours: int = Field(default=0, ge=0)
    semester: Optional[int] = Field(default=None, ge=1, le=8)
    is_mandatory: bool = True
    career_track: str = "GENERAL"
    description: Optional[str] = None

    @field_validator("course_code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("career_track")
    @classmethod
    def validate_track(cls, value: str) -> str:
        track = value.strip().upper()
        if track not in CAREER_TRACKS:
            raise ValueError(f"career_track must be one of {CAREER_TRACKS}")
        return track


class CourseUpdate(BaseModel):
    course_code: Optional[str] = Field(default=None, min_length=2, max_length=20)
    course_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    credits: Optional[int] = Field(default=None, gt=0)
    theory_hours: Optional[int] = Field(default=None, ge=0)
    practice_hours: Optional[int] = Field(default=None, ge=0)
    semester: Optional[int] = Field(default=None, ge=1, le=8)
    is_mandatory: Optional[bool] = None
    career_track: Optional[str] = None
    description: Optional[str] = None

    @field_validator("course_code")
    @classmethod
    def normalize_code(cls, value: Optional[str]) -> Optional[str]:
        return value.strip().upper() if value else value

    @field_validator("career_track")
    @classmethod
    def validate_track(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        track = value.strip().upper()
        if track not in CAREER_TRACKS:
            raise ValueError(f"career_track must be one of {CAREER_TRACKS}")
        return track


class CourseResponse(BaseModel):
    id: str
    course_code: str
    course_name: str
    credits: int
    theory_hours: int = 0
    practice_hours: int = 0
    semester: Optional[int] = None
    is_mandatory: bool = True
    career_track: str = "GENERAL"
    description: Optional[str] = None
    created_at: Optional[object] = None
    updated_at: Optional[object] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class PrerequisiteCreate(BaseModel):
    prerequisite_course_id: str
    relation_type: str = "PREREQUISITE"

    @field_validator("relation_type")
    @classmethod
    def validate_relation(cls, value: str) -> str:
        rel = value.strip().upper()
        if rel not in RELATION_TYPES:
            raise ValueError(f"relation_type must be one of {RELATION_TYPES}")
        return rel


class PrerequisiteEdge(BaseModel):
    course_id: Optional[str] = None
    prerequisite_course_id: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    prerequisite_code: Optional[str] = None
    prerequisite_name: Optional[str] = None
    relation_type: str
    depth: Optional[int] = None

    model_config = ConfigDict(extra="ignore")


class CoursePrerequisitesResponse(BaseModel):
    course_id: str
    course_code: str
    course_name: str
    hard: List[PrerequisiteEdge] = Field(default_factory=list)
    soft: List[PrerequisiteEdge] = Field(default_factory=list)
    closure: List[PrerequisiteEdge] = Field(default_factory=list)
    blocked_reason: Optional[str] = None


class RecordUpsert(BaseModel):
    user_id: str
    course_code: str
    status: str
    grade: Optional[float] = Field(default=None, ge=0, le=10)
    semester_taken: Optional[str] = None
    attempt_count: Optional[int] = Field(default=None, ge=1)

    @field_validator("course_code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        status = value.strip().upper()
        if status not in RECORD_STATUSES:
            raise ValueError(f"status must be one of {RECORD_STATUSES}")
        return status


class RecordResponse(BaseModel):
    id: str
    user_id: str
    course_id: str
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    credits: Optional[int] = None
    status: str
    grade: Optional[float] = None
    semester_taken: Optional[str] = None
    attempt_count: int = 1
    recorded_at: Optional[object] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class TranscriptResponse(BaseModel):
    user_id: str
    student_code: Optional[str] = None
    full_name: Optional[str] = None
    records: List[RecordResponse] = Field(default_factory=list)


class EligibleCourse(BaseModel):
    course_id: str
    course_code: str
    course_name: str
    credits: Optional[int] = None
    semester: Optional[int] = None
    career_track: Optional[str] = None
    is_mandatory: Optional[bool] = None
    missing_prereq_codes: List[str] = Field(default_factory=list)
    recommended_previous: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class EligibleCoursesResponse(BaseModel):
    user_id: str
    student_code: Optional[str] = None
    courses: List[EligibleCourse] = Field(default_factory=list)


class CsvImportError(BaseModel):
    row: int
    reason: str


class CsvImportResponse(BaseModel):
    imported: int = 0
    errors: List[CsvImportError] = Field(default_factory=list)
    total: int = 0


class MaterialCreate(BaseModel):
    course_id: str
    file_id: Optional[str] = None
    title: Optional[str] = Field(default=None, max_length=255)
    material_type: str
    file_url: Optional[str] = None
    dataset_id: Optional[str] = None

    @field_validator("material_type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        kind = value.strip().upper()
        if kind not in MATERIAL_TYPES:
            raise ValueError(f"material_type must be one of {MATERIAL_TYPES}")
        return kind


class MaterialUpdate(BaseModel):
    course_id: Optional[str] = None
    title: Optional[str] = Field(default=None, max_length=255)
    material_type: Optional[str] = None
    file_url: Optional[str] = None
    file_id: Optional[str] = None
    dataset_id: Optional[str] = None

    @field_validator("material_type")
    @classmethod
    def validate_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        kind = value.strip().upper()
        if kind not in MATERIAL_TYPES:
            raise ValueError(f"material_type must be one of {MATERIAL_TYPES}")
        return kind


class MaterialResponse(BaseModel):
    id: str
    course_id: str
    title: str
    material_type: str
    file_url: Optional[str] = None
    qdrant_point_id: Optional[str] = None
    file_id: Optional[str] = None
    dataset_id: Optional[str] = None
    created_at: Optional[object] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class AcademicFactsDebug(BaseModel):
    """Thin debug payload. Full AcademicFactsService is PR3."""

    student_id: str
    student_code: Optional[str] = None
    full_name: Optional[str] = None
    records: List[RecordResponse] = Field(default_factory=list)
    eligible_courses: List[EligibleCourse] = Field(default_factory=list)
    blocked_sample: List[dict] = Field(default_factory=list)
