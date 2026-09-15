"""P0 cache isolation for hybrid advisor (LLM/Qdrant mocked)."""
import sys
import types
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

for name in (
    "qdrant_client",
    "qdrant_client.http",
    "qdrant_client.http.models",
    "qdrant_client.models",
    "sentence_transformers",
):
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = []
        sys.modules[name] = mod

sys.modules["sentence_transformers"].SentenceTransformer = MagicMock
sys.modules["sentence_transformers"].CrossEncoder = MagicMock
sys.modules["qdrant_client"].QdrantClient = MagicMock
http_models = sys.modules["qdrant_client.http.models"]
sys.modules["qdrant_client.http"].models = http_models
sys.modules["qdrant_client"].models = http_models
for attr in (
    "Distance",
    "VectorParams",
    "PointStruct",
    "Filter",
    "FieldCondition",
    "MatchAny",
    "MatchValue",
    "FilterSelector",
):
    setattr(http_models, attr, MagicMock)

from app.core.config import settings
from app.services.academic_facts_service import AcademicFacts
from app.services.cache_service import semantic_cache_service
from app.services.chat_service import ChatService, build_cache_suffix
from app.services.intent_classifier import ChatIntent, IntentClassifier


def test_hybrid_suffix_contains_user_and_differs_per_user():
    q = "em nên học gì"
    a = build_cache_suffix("HYBRID", "bot1", "user-a")
    b = build_cache_suffix("HYBRID", "bot1", "user-b")
    assert a != b
    assert "user_" in a and "user_" in b
    assert "user-a" in a and "user-b" in b
    assert build_cache_suffix("COURSE_ADVICE", "bot1", "user-a") is None
    assert "user_" not in build_cache_suffix("MATERIAL_QA", "bot1", "user-a", "course-1")
    del q


def _facts(user_id: str, empty: bool = False) -> AcademicFacts:
    if empty:
        return AcademicFacts.empty(user_id, student_code="SVNEW", full_name="New")
    return AcademicFacts(
        student_id=user_id,
        student_code="SV001",
        full_name="Lê Hải Đăng",
        current_semester="2025-1",
        current_semester_source="IN_PROGRESS",
        empty_transcript=False,
        records=[{"course_code": "INT1203", "course_name": "Kiến trúc máy tính", "status": "FAILED", "credits": 3}],
        retake=[{"course_code": "INT1203", "course_name": "Kiến trúc máy tính", "status": "FAILED", "credits": 3}],
    )


def _service(monkeypatch, facts: AcademicFacts) -> ChatService:
    monkeypatch.setattr(settings, "academic_facts_enabled", True)
    monkeypatch.setattr(settings, "semantic_cache_enabled", True)
    monkeypatch.setattr(settings, "chat_fast_path", True)
    facts_svc = AsyncMock()
    facts_svc.build = AsyncMock(return_value=facts)
    facts_svc.course_repo = AsyncMock()
    facts_svc.course_repo.get_by_code = AsyncMock(return_value=None)
    svc = ChatService(
        dataset_repo=AsyncMock(),
        dataset_file_repo=AsyncMock(),
        chunk_repo=AsyncMock(),
        session_repo=None,
        chatbot_repo=None,
        file_repo=None,
        academic_facts_service=facts_svc,
        intent_classifier_svc=IntentClassifier(),
    )
    svc._try_embed_question = MagicMock(return_value=np.ones(8, dtype=float))
    svc._generate_answer = AsyncMock(return_value="Câu trả lời cố vấn học tập hợp lệ.")
    svc._search_dataset = AsyncMock(
        return_value={
            "dataset_id": "d1",
            "dataset_name": "docs",
            "files": ["a.pdf"],
            "results": [
                {
                    "text": "slide web",
                    "score": 0.9,
                    "file_name": "a.pdf",
                    "file_id": "f1",
                    "chunk_index": 0,
                    "cite": "[d1:f1:0]",
                }
            ],
            "error": None,
        }
    )
    return svc


@pytest.mark.asyncio
async def test_hybrid_cache_keys_do_not_leak_across_users(monkeypatch):
    semantic_cache_service.clear()
    set_suffixes = []
    get_suffixes = []
    real_set = semantic_cache_service.set
    real_get = semantic_cache_service.get

    def spy_set(question, embedding, answer, suffix="", ttl_seconds=None):
        set_suffixes.append(suffix)
        return real_set(question, embedding, answer, suffix=suffix, ttl_seconds=ttl_seconds)

    def spy_get(question, embedding, suffix=""):
        get_suffixes.append(suffix)
        return real_get(question, embedding, suffix=suffix)

    monkeypatch.setattr("app.services.chat_service.semantic_cache_service.set", spy_set)
    monkeypatch.setattr("app.services.chat_service.semantic_cache_service.get", spy_get)

    question = "em hỏi chung về khoa"
    svc_a = _service(monkeypatch, _facts("user-a"))
    svc_b = _service(monkeypatch, _facts("user-b"))
    await svc_a.ask_question(question, ["d1"], user_context={"id": "user-a", "role": "student"})
    await svc_b.ask_question(question, ["d1"], user_context={"id": "user-b", "role": "student"})

    assert set_suffixes
    assert set_suffixes[0] != set_suffixes[1]
    assert "user_" in set_suffixes[0] and "user_" in set_suffixes[1]
    assert "user-a" in set_suffixes[0] and "user-b" in set_suffixes[1]
    assert all("user_" in suffix for suffix in get_suffixes)


@pytest.mark.asyncio
async def test_course_advice_never_cache_get_or_set(monkeypatch):
    semantic_cache_service.clear()
    get_mock = MagicMock(return_value=None)
    set_mock = MagicMock()
    monkeypatch.setattr("app.services.chat_service.semantic_cache_service.get", get_mock)
    monkeypatch.setattr("app.services.chat_service.semantic_cache_service.set", set_mock)

    svc = _service(monkeypatch, _facts("user-a"))
    result = await svc.ask_question(
        "tiên quyết của OOP là gì?",
        ["d1"],
        user_context={"id": "user-a", "role": "student"},
    )
    get_mock.assert_not_called()
    set_mock.assert_not_called()
    svc._try_embed_question.assert_not_called()
    svc._search_dataset.assert_not_called()
    assert result["intent"] == ChatIntent.COURSE_ADVICE.value


@pytest.mark.asyncio
async def test_empty_transcript_flag_on_response(monkeypatch):
    semantic_cache_service.clear()
    svc = _service(monkeypatch, _facts("user-new", empty=True))
    result = await svc.ask_question(
        "tiên quyết môn nào?",
        ["d1"],
        user_context={"id": "user-new", "role": "student"},
    )
    assert result["empty_transcript"] is True
    assert result["debug"]["empty_transcript"] is True
    assert result["intent"] == ChatIntent.COURSE_ADVICE.value
