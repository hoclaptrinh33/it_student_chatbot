import asyncio
import logging

from app.core.database import SessionLocal
from app.models.enums import DatasetFileStatus
from app.repositories import DatasetFileRepository, FileRepository, ChunkRepository
from app.services.processing_service import ProcessingService

logger = logging.getLogger(__name__)


async def _async_process(dataset_id: str, dataset_file_id: str):
    """One Postgres session per ingest job. Commit success and ERROR status; do not roll back the UI status row."""
    async with SessionLocal() as session:
        dataset_file_repo = DatasetFileRepository(session)
        file_repo = FileRepository(session)
        chunk_repo = ChunkRepository(session)
        service = ProcessingService(
            dataset_file_repo=dataset_file_repo,
            file_repo=file_repo,
            chunk_repo=chunk_repo,
        )
        try:
            await service.process_dataset_file(dataset_id, dataset_file_id)
            await session.commit()
        except Exception:
            logger.exception("Job Failed for dataset_file=%s", dataset_file_id)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                async with SessionLocal() as err_session:
                    await DatasetFileRepository(err_session).update_status(
                        dataset_file_id, DatasetFileStatus.ERROR
                    )
                    await err_session.commit()
            raise


def process_dataset_file_job(dataset_id: str, dataset_file_id: str):
    """
    Sync entrypoint for RQ Worker
    """
    asyncio.run(_async_process(dataset_id, dataset_file_id))
