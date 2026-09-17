import asyncio
import logging
from typing import Optional

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.models.enums import DatasetFileStatus
from app.repositories import (
    ChunkRepository,
    CourseRepository,
    DatasetFileRepository,
    FileRepository,
    LearningMaterialRepository,
)
from app.services.processing_service import ProcessingService

logger = logging.getLogger(__name__)

async def _async_process(
    dataset_id: str,
    dataset_file_id: str,
    course_id: Optional[str] = None,
    material_type: Optional[str] = None,
):
    """One Postgres session per ingest job with NullPool created within the active event loop."""
    worker_engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
    )
    WorkerSession = async_sessionmaker(worker_engine, expire_on_commit=False, class_=AsyncSession)
    try:
        async with WorkerSession() as session:
            dataset_file_repo = DatasetFileRepository(session)
            file_repo = FileRepository(session)
            chunk_repo = ChunkRepository(session)
            service = ProcessingService(
                dataset_file_repo=dataset_file_repo,
                file_repo=file_repo,
                chunk_repo=chunk_repo,
                material_repo=LearningMaterialRepository(session),
                course_repo=CourseRepository(session),
            )
            try:
                await service.process_dataset_file(
                    dataset_id,
                    dataset_file_id,
                    course_id=course_id,
                    material_type=material_type,
                )
                await session.commit()
            except Exception:
                logger.exception("Job Failed for dataset_file=%s", dataset_file_id)
                try:
                    await session.commit()
                except Exception:
                    await session.rollback()
                    async with WorkerSession() as err_session:
                        await DatasetFileRepository(err_session).update_status(
                            dataset_file_id, DatasetFileStatus.ERROR
                        )
                        await err_session.commit()
                raise
    finally:
        await worker_engine.dispose()


def process_dataset_file_job(
    dataset_id: str,
    dataset_file_id: str,
    course_id: Optional[str] = None,
    material_type: Optional[str] = None,
):
    """
    Sync entrypoint for RQ Worker
    """
    asyncio.run(_async_process(dataset_id, dataset_file_id, course_id, material_type))
