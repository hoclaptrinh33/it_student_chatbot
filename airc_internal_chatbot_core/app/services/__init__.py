"""
Services package - Business logic layer
"""

__all__ = [
    "DatasetService",
    "ChatService",
    "chunking_service",
    "rerank_service",
    "semantic_cache_service",
    "CourseService",
    "PrerequisiteService",
    "StudentRecordService",
    "LearningMaterialService",
]


def __getattr__(name):
    if name == "DatasetService":
        from app.services.dataset_service import DatasetService
        return DatasetService
    if name == "ChatService":
        from app.services.chat_service import ChatService
        return ChatService
    if name == "chunking_service":
        from app.services.chunking_service import chunking_service
        return chunking_service
    if name == "rerank_service":
        from app.services.rerank_service import rerank_service
        return rerank_service
    if name == "semantic_cache_service":
        from app.services.cache_service import semantic_cache_service
        return semantic_cache_service
    if name == "CourseService":
        from app.services.course_service import CourseService
        return CourseService
    if name == "PrerequisiteService":
        from app.services.prerequisite_service import PrerequisiteService
        return PrerequisiteService
    if name == "StudentRecordService":
        from app.services.student_record_service import StudentRecordService
        return StudentRecordService
    if name == "LearningMaterialService":
        from app.services.learning_material_service import LearningMaterialService
        return LearningMaterialService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

