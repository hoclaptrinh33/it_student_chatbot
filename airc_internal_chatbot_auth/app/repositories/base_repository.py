"""
Base Repository - UUID parse + row serialization for dict APIs
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base repository with UUID helpers. Repositories return dicts with id: str."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def parse_id(id_str: str) -> Optional[UUID]:
        """UUID only. A Mongo 24-hex ObjectId is invalid."""
        if id_str is None:
            return None
        try:
            return UUID(str(id_str))
        except (ValueError, TypeError, AttributeError):
            return None

    @staticmethod
    def serialize_value(value: Any) -> Any:
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: BaseRepository.serialize_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [BaseRepository.serialize_value(v) for v in value]
        return value

    @staticmethod
    def serialize_row(row) -> Optional[dict]:
        if row is None:
            return None
        if isinstance(row, dict):
            data = dict(row)
        elif hasattr(row, "__table__"):
            data = {c.name: getattr(row, c.name) for c in row.__table__.columns}
        else:
            data = {k: v for k, v in vars(row).items() if not k.startswith("_")}
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id")
        return {k: BaseRepository.serialize_value(v) for k, v in data.items()}

    @staticmethod
    def serialize_rows(rows) -> list:
        return [BaseRepository.serialize_row(r) for r in rows if r is not None]
