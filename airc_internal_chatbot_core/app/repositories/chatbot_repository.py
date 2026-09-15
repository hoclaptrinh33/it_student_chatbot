"""
Chatbot Repository - Data access layer cho chatbots
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete, select

from app.models.orm import Chatbot, ChatbotDataset
from app.repositories.base_repository import BaseRepository


class ChatbotRepository(BaseRepository):
    """Repository cho Chatbot operations với RBAC"""

    def __init__(self, session):
        super().__init__(session)

    async def _dataset_ids_for(self, chatbot_id: UUID) -> List[str]:
        result = await self.session.execute(
            select(ChatbotDataset.dataset_id).where(ChatbotDataset.chatbot_id == chatbot_id)
        )
        return [str(row[0]) for row in result.all()]

    async def _hydrate(self, row: Chatbot) -> dict:
        doc = self.serialize_row(row)
        doc["dataset_ids"] = await self._dataset_ids_for(row.id)
        if doc.get("owner_id") is None:
            doc["owner_id"] = ""
        return doc

    async def _replace_datasets(self, chatbot_id: UUID, dataset_ids: List[str]) -> None:
        await self.session.execute(
            delete(ChatbotDataset).where(ChatbotDataset.chatbot_id == chatbot_id)
        )
        for raw in dataset_ids:
            ds_id = self.parse_id(raw)
            if ds_id:
                self.session.add(ChatbotDataset(chatbot_id=chatbot_id, dataset_id=ds_id))
        await self.session.flush()

    async def create_chatbot(
        self,
        name: str,
        description: Optional[str],
        icon: Optional[str],
        config: Dict[str, Any],
        dataset_ids: List[str],
        allowed_roles: List[str],
        visibility: str,
        owner_id: str,
    ) -> dict:
        owner_uuid = self.parse_id(owner_id)
        row = Chatbot(
            name=name,
            description=description,
            icon=icon,
            config=config or {},
            allowed_roles=allowed_roles or [],
            visibility=visibility,
            owner_id=owner_uuid,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=None,
        )
        self.session.add(row)
        await self.session.flush()
        await self._replace_datasets(row.id, dataset_ids)
        return await self._hydrate(row)

    async def get_by_id(self, chatbot_id: str) -> Optional[dict]:
        uid = self.parse_id(chatbot_id)
        if not uid:
            return None
        row = await self.session.get(Chatbot, uid)
        if not row:
            return None
        return await self._hydrate(row)

    async def get_by_owner(self, owner_id: str) -> List[dict]:
        uid = self.parse_id(owner_id)
        if not uid:
            return []
        result = await self.session.execute(
            select(Chatbot).where(Chatbot.owner_id == uid).order_by(Chatbot.created_at.desc())
        )
        return [await self._hydrate(row) for row in result.scalars().all()]

    async def get_available_for_role(self, role: str) -> List[dict]:
        result = await self.session.execute(
            select(Chatbot)
            .where(Chatbot.is_active.is_(True), Chatbot.allowed_roles.contains([role]))
            .order_by(Chatbot.created_at.desc())
        )
        return [await self._hydrate(row) for row in result.scalars().all()]

    async def get_all(self, is_active: Optional[bool] = None) -> List[dict]:
        stmt = select(Chatbot)
        if is_active is not None:
            stmt = stmt.where(Chatbot.is_active.is_(is_active))
        stmt = stmt.order_by(Chatbot.created_at.desc())
        result = await self.session.execute(stmt)
        return [await self._hydrate(row) for row in result.scalars().all()]

    async def update_chatbot(self, chatbot_id: str, update_data: Dict[str, Any]) -> bool:
        uid = self.parse_id(chatbot_id)
        if not uid:
            return False
        row = await self.session.get(Chatbot, uid)
        if not row:
            return False
        payload = dict(update_data)
        dataset_ids = payload.pop("dataset_ids", None)
        payload["updated_at"] = datetime.utcnow()
        if "owner_id" in payload:
            payload["owner_id"] = self.parse_id(payload["owner_id"]) if payload["owner_id"] else None
        for key, value in payload.items():
            if hasattr(row, key):
                setattr(row, key, value)
        if dataset_ids is not None:
            await self._replace_datasets(uid, dataset_ids)
        await self.session.flush()
        return True

    async def assign_datasets(self, chatbot_id: str, dataset_ids: List[str]) -> bool:
        return await self.update_chatbot(chatbot_id, {"dataset_ids": dataset_ids})

    async def delete_chatbot(self, chatbot_id: str) -> bool:
        uid = self.parse_id(chatbot_id)
        if not uid:
            return False
        row = await self.session.get(Chatbot, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True

    async def set_active(self, chatbot_id: str, is_active: bool) -> bool:
        return await self.update_chatbot(chatbot_id, {"is_active": is_active})

    async def get_roles_with_chatbot_assigned(self, exclude_chatbot_id: Optional[str] = None) -> List[str]:
        stmt = select(Chatbot).where(Chatbot.is_active.is_(True))
        exclude = self.parse_id(exclude_chatbot_id) if exclude_chatbot_id else None
        if exclude:
            stmt = stmt.where(Chatbot.id != exclude)
        result = await self.session.execute(stmt)
        roles = set()
        for row in result.scalars().all():
            for role in row.allowed_roles or []:
                if role and role.lower() != "admin":
                    roles.add(role.lower())
        return list(roles)
