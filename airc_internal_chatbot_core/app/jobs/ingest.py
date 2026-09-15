import asyncio
import logging

from app.core.database import SessionLocal
from app.repositories import DatasetFileRepository, FileRepository, ChunkRepository
from app.services.processing_service import ProcessingService

logger = logging.getLogger(__name__)


async def _async_process(dataset_id: str, dataset_file_id: str):
    """Open one Postgres session for the ingest job and commit on success."""
    async with SessionLocal() as session:
        try:
            dataset_file_repo = DatasetFileRepository(session)
            file_repo = FileRepository(session)
            chunk_repo = ChunkRepository(session)
            service = ProcessingService(
                dataset_file_repo=dataset_file_repo,
                file_repo=file_repo,
                chunk_repo=chunk_repo,
            )
            await service.process_dataset_file(dataset_id, dataset_file_id)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception("Job Failed for dataset_file=%s: %s", dataset_file_id, e)
            raise


def process_dataset_file_job(dataset_id: str, dataset_file_id: str):
    """
    Sync entrypoint for RQ Worker
    """
    asyncio.run(_async_process(dataset_id, dataset_file_id))
