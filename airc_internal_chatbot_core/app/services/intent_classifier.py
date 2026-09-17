"""Rules-first chat intent classifier for the academic advisor."""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class ChatIntent(str, Enum):
    COURSE_ADVICE = "COURSE_ADVICE"
    MATERIAL_QA = "MATERIAL_QA"
    HYBRID = "HYBRID"
    GREETING = "GREETING"


def fold_vi(text: str) -> str:
    """Lowercase and strip combining marks so 'quyết'/'đề' match 'quyet'/'de'."""
    normalized = unicodedata.normalize("NFD", text or "")
    folded = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn").lower()
    return folded.replace("đ", "d")


# Patterns are matched against fold_vi(question).
COURSE_PATTERNS = [
    r"tien quyet",
    r"hoc\s*lai",
    r"truot",
    r"dang\s*ky",
    r"lo\s*trinh",
    r"tin\s*chi",
    r"hoc\s*k[iy]",
    r"nen\s*hoc",
    r"duoc\s*hoc",
    r"du dieu kien",
    r"mon nao",
    r"hoc mon",
    r"dinh huong",
    r"dev web",
    r"huong\s*(web|ai|security|data|mang)",
    r"career",
    r"chuyen nganh",
    r"tinh hinh",
    r"hoc tap",
    r"bang diem",
    r"diem so",
    r"ket qua",
    r"hoc luc",
    r"hoc vu",
    r"dang hoc",
    r"mon dang",
    r"\bgpa\b",
    r"transcript",
]
MATERIAL_PATTERNS = [
    r"slide",
    r"de cuong",
    r"giao trinh",
    r"de thi",
    r"tai lieu",
    r"bai giang",
    r"syllabus",
    r"noi dung mon",
    r"hoc gi trong",
    r"chapter",
    r"chuong",
]
TRACK_HINTS = {
    "WEB": [r"\bweb\b", r"frontend", r"backend", r"dev web", r"full\s*stack"],
    "AI": [r"\bai\b", r"hoc may", r"machine learning", r"deep learning", r"nlp"],
    "SECURITY": [r"an toan", r"an ninh", r"security", r"pentest"],
    "DATA": [r"du lieu", r"database", r"sql", r"data"],
    "NETWORK": [r"mang may tinh", r"mang", r"cloud", r"kubernetes"],
    "SOFTWARE": [r"phan mem", r"oop", r"cong nghe phan mem"],
}

COURSE_CODE_RE = re.compile(r"INT\d{4}", re.IGNORECASE)
GREETING_PATTERNS = [
    r"^(em\s+)?(xin\s*)?chao(\s+\w+){0,4}[\s!.,?]*$",
    r"^(hello|hi|hey|alo)([\s!.,?]|$)",
]


@dataclass
class ClassifiedIntent:
    intent: ChatIntent
    career_track: Optional[str] = None
    course_codes: List[str] = field(default_factory=list)
    matched_course: bool = False
    matched_material: bool = False


class IntentClassifier:
    """Rules first. Optional LLM only fills track/codes when the question is ambiguous."""

    def classify(self, question: str, history: Optional[list] = None) -> ClassifiedIntent:
        del history  # rules use the current question only
        q = fold_vi(question or "")
        matched_course = any(re.search(pattern, q, re.I) for pattern in COURSE_PATTERNS)
        matched_material = any(re.search(pattern, q, re.I) for pattern in MATERIAL_PATTERNS)
        is_greeting = any(re.search(pattern, q.strip(), re.I) for pattern in GREETING_PATTERNS)
        if matched_course and matched_material:
            intent = ChatIntent.HYBRID
        elif matched_course:
            intent = ChatIntent.COURSE_ADVICE
        elif matched_material:
            intent = ChatIntent.MATERIAL_QA
        elif is_greeting:
            intent = ChatIntent.GREETING
        else:
            # Advisor-first: unmatched questions use AcademicFacts, not RAG-reject.
            intent = ChatIntent.COURSE_ADVICE
        return ClassifiedIntent(
            intent=intent,
            career_track=self._detect_track(q),
            course_codes=self._extract_course_codes(question or ""),
            matched_course=matched_course,
            matched_material=matched_material,
        )

    async def classify_async(self, question: str, history: Optional[list] = None) -> ClassifiedIntent:
        result = self.classify(question, history)
        if self._is_ambiguous(result) and not settings.chat_fast_path:
            await self._llm_enrich(result, question or "")
        return result

    def _is_ambiguous(self, result: ClassifiedIntent) -> bool:
        return (
            result.intent == ChatIntent.HYBRID
            and not result.matched_course
            and not result.matched_material
            and result.career_track is None
            and not result.course_codes
        )

    def _detect_track(self, q: str) -> Optional[str]:
        for track, patterns in TRACK_HINTS.items():
            if any(re.search(pattern, q, re.I) for pattern in patterns):
                return track
        return None

    @staticmethod
    def _extract_course_codes(question: str) -> List[str]:
        seen = []
        for match in COURSE_CODE_RE.findall(question or ""):
            code = match.upper()
            if code not in seen:
                seen.append(code)
        return seen

    async def _llm_enrich(self, result: ClassifiedIntent, question: str) -> None:
        """Fill career_track / course_codes only. Never overwrite a rules intent."""
        try:
            from app.services.llm_service import llm_service

            raw = await llm_service.generate(
                (
                    "Phân loại câu hỏi cố vấn học tập. Chỉ trả JSON "
                    '{"career_track":"WEB|AI|SECURITY|DATA|NETWORK|SOFTWARE|null",'
                    '"course_codes":["INT1234"]}.\n'
                    f"Câu hỏi: {question}"
                ),
                temperature=0.0,
                max_tokens=64,
                timeout=5.0,
            )
            track, codes = _parse_enrichment(raw)
            if result.career_track is None and track:
                result.career_track = track
            if not result.course_codes and codes:
                result.course_codes = codes
        except Exception as exc:
            logger.info("[INTENT] LLM classify skipped: %s", exc)


def _parse_enrichment(raw: str) -> tuple[Optional[str], List[str]]:
    if not raw:
        return None, []
    track = None
    for name in TRACK_HINTS:
        if re.search(rf'"{name}"', raw, re.I) or re.search(rf"\b{name}\b", raw, re.I):
            track = name
            break
    codes = []
    for match in COURSE_CODE_RE.findall(raw):
        code = match.upper()
        if code not in codes:
            codes.append(code)
    return track, codes


intent_classifier = IntentClassifier()
