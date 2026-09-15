"""
User Repository - Data access layer for users
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.orm import Role, User, UserRole
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository cho User operations"""

    def __init__(self, session):
        super().__init__(session, User)

    async def _upsert_user_role(self, user_id: UUID, role_code: str) -> None:
        result = await self.session.execute(select(Role).where(Role.code == role_code))
        role = result.scalar_one_or_none()
        if not role:
            return
        stmt = (
            pg_insert(UserRole)
            .values(user_id=user_id, role_id=role.id, assigned_at=datetime.utcnow())
            .on_conflict_do_nothing(index_elements=["user_id", "role_id"])
        )
        await self.session.execute(stmt)

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        role: str = "student",
        student_code: Optional[str] = None,
        department: Optional[str] = "Khoa CNTT",
    ) -> dict:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            student_code=student_code,
            department=department,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self.session.add(user)
        await self.session.flush()
        await self._upsert_user_role(user.id, role)
        return self.serialize_row(user)

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        uid = self.parse_id(user_id)
        if not uid:
            return None
        user = await self.session.get(User, uid)
        return self.serialize_row(user)

    async def get_by_email(self, email: str) -> Optional[dict]:
        result = await self.session.execute(select(User).where(User.email == email))
        return self.serialize_row(result.scalar_one_or_none())

    async def email_exists(self, email: str) -> bool:
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.email == email)
        )
        return (result.scalar_one() or 0) > 0

    async def update_user(self, user_id: str, update_data: dict) -> bool:
        uid = self.parse_id(user_id)
        if not uid:
            return False
        user = await self.session.get(User, uid)
        if not user:
            return False
        update_data = dict(update_data)
        update_data["updated_at"] = datetime.utcnow()
        role_code = update_data.get("role")
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        if role_code:
            await self._upsert_user_role(uid, role_code)
        await self.session.flush()
        return True

    async def get_all_users(self, limit: int = 100) -> List[dict]:
        result = await self.session.execute(select(User).limit(limit))
        return self.serialize_rows(result.scalars().all())

    async def delete_user(self, user_id: str) -> bool:
        uid = self.parse_id(user_id)
        if not uid:
            return False
        user = await self.session.get(User, uid)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.flush()
        return True

    async def get_role_code(self, user_id: str) -> Optional[str]:
        uid = self.parse_id(user_id)
        if not uid:
            return None
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == uid,
                Role.is_active.is_(True),
                (UserRole.expires_at.is_(None)) | (UserRole.expires_at > now),
            )
        )
        codes = [row[0] for row in result.all()]
        if codes:
            for preferred in ("admin", "teacher", "student"):
                if preferred in codes:
                    return preferred
            return codes[0]
        user = await self.session.get(User, uid)
        if user and user.role:
            return user.role
        return None
