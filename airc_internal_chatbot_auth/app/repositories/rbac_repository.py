"""
RBAC Repository - SQLAlchemy access for permissions, roles, and assignments
"""
from datetime import datetime
from typing import List, Optional
import logging

from sqlalchemy import delete, func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.orm import Permission, Role, RolePermission, User, UserRole
from app.models.rbac import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    RoleWithPermissions,
)
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class RBACRepository:
    """Repository xử lý tất cả database operations cho RBAC"""

    def __init__(self, session):
        self.session = session

    def _perm_response(self, row: Permission) -> PermissionResponse:
        data = BaseRepository.serialize_row(row)
        data["_id"] = data["id"]
        data.setdefault("updated_at", None)
        return PermissionResponse(**data)

    async def _perm_count(self, role_id) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(RolePermission)
            .where(RolePermission.role_id == role_id)
        )
        return int(result.scalar_one() or 0)

    def _role_response(self, row: Role, permission_count: int = 0) -> RoleResponse:
        data = BaseRepository.serialize_row(row)
        data["_id"] = data["id"]
        data["permission_count"] = permission_count
        return RoleResponse(**data)

    # ==================== PERMISSIONS ====================

    async def create_permission(
        self,
        perm: PermissionCreate,
        created_by: Optional[str] = None,
    ) -> PermissionResponse:
        row = Permission(
            name=perm.name,
            code=perm.code,
            resource=perm.resource,
            action=perm.action,
            scope=perm.scope,
            description=perm.description,
            is_system=perm.is_system,
            created_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        logger.info("Created permission: %s", perm.code)
        return self._perm_response(row)

    async def get_all_permissions(self, include_system: bool = True) -> List[PermissionResponse]:
        stmt = select(Permission)
        if not include_system:
            stmt = stmt.where(Permission.is_system.is_(False))
        result = await self.session.execute(stmt)
        return [self._perm_response(row) for row in result.scalars().all()]

    async def get_permission_by_id(self, permission_id: str) -> Optional[PermissionResponse]:
        uid = BaseRepository.parse_id(permission_id)
        if not uid:
            return None
        row = await self.session.get(Permission, uid)
        return self._perm_response(row) if row else None

    async def get_permission_by_code(self, code: str) -> Optional[PermissionResponse]:
        result = await self.session.execute(select(Permission).where(Permission.code == code))
        row = result.scalar_one_or_none()
        return self._perm_response(row) if row else None

    async def update_permission(
        self,
        permission_id: str,
        update_data: PermissionUpdate,
    ) -> Optional[PermissionResponse]:
        uid = BaseRepository.parse_id(permission_id)
        if not uid:
            return None
        row = await self.session.get(Permission, uid)
        if not row:
            return None
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(row, key):
                setattr(row, key, value)
        await self.session.flush()
        return self._perm_response(row)

    async def delete_permission(self, permission_id: str) -> bool:
        perm = await self.get_permission_by_id(permission_id)
        if not perm or perm.is_system:
            return False
        uid = BaseRepository.parse_id(permission_id)
        await self.session.execute(delete(RolePermission).where(RolePermission.permission_id == uid))
        row = await self.session.get(Permission, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True

    # ==================== ROLES ====================

    async def create_role(
        self,
        role: RoleCreate,
        created_by: Optional[str] = None,
    ) -> RoleResponse:
        row = Role(
            name=role.name,
            code=role.code,
            description=role.description,
            is_system=role.is_system,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        logger.info("Created role: %s", role.code)
        return self._role_response(row, 0)

    async def get_all_roles(self, include_inactive: bool = False) -> List[RoleResponse]:
        stmt = select(Role)
        if not include_inactive:
            stmt = stmt.where(Role.is_active.is_(True))
        result = await self.session.execute(stmt)
        roles = result.scalars().all()
        out = []
        for role in roles:
            out.append(self._role_response(role, await self._perm_count(role.id)))
        return out

    async def get_role_by_id(self, role_id: str) -> Optional[RoleResponse]:
        uid = BaseRepository.parse_id(role_id)
        if not uid:
            return None
        row = await self.session.get(Role, uid)
        if not row:
            return None
        return self._role_response(row, await self._perm_count(uid))

    async def get_role_by_code(self, code: str) -> Optional[RoleResponse]:
        result = await self.session.execute(select(Role).where(Role.code == code))
        row = result.scalar_one_or_none()
        if not row:
            return None
        return self._role_response(row, await self._perm_count(row.id))

    async def get_role_with_permissions(self, role_id: str) -> Optional[RoleWithPermissions]:
        uid = BaseRepository.parse_id(role_id)
        if not uid:
            return None
        row = await self.session.get(Role, uid)
        if not row:
            return None
        result = await self.session.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == uid)
        )
        perms = [self._perm_response(p) for p in result.scalars().all()]
        base = self._role_response(row, len(perms))
        return RoleWithPermissions(**base.model_dump(by_alias=True), permissions=perms)

    async def update_role(self, role_id: str, update_data: RoleUpdate) -> Optional[RoleResponse]:
        uid = BaseRepository.parse_id(role_id)
        if not uid:
            return None
        row = await self.session.get(Role, uid)
        if not row:
            return None
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(row, key):
                setattr(row, key, value)
        row.updated_at = datetime.utcnow()
        await self.session.flush()
        return self._role_response(row, await self._perm_count(uid))

    async def delete_role(self, role_id: str) -> bool:
        role = await self.get_role_by_id(role_id)
        if not role or role.is_system:
            return False
        uid = BaseRepository.parse_id(role_id)
        await self.session.execute(delete(RolePermission).where(RolePermission.role_id == uid))
        await self.session.execute(delete(UserRole).where(UserRole.role_id == uid))
        row = await self.session.get(Role, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True

    # ==================== ROLE-PERMISSION MAPPING ====================

    async def grant_permissions_to_role(
        self,
        role_id: str,
        permission_ids: List[str],
        granted_by: Optional[str] = None,
    ):
        rid = BaseRepository.parse_id(role_id)
        if not rid or not permission_ids:
            return
        values = []
        for pid in permission_ids:
            puid = BaseRepository.parse_id(pid)
            if puid:
                values.append({"role_id": rid, "permission_id": puid})
        if not values:
            return
        stmt = pg_insert(RolePermission).values(values).on_conflict_do_nothing()
        await self.session.execute(stmt)
        logger.info("Granted %s permissions to role %s", len(permission_ids), role_id)

    async def set_role_permissions(
        self,
        role_id: str,
        permission_ids: List[str],
        assigned_by: Optional[str] = None,
    ):
        rid = BaseRepository.parse_id(role_id)
        if not rid:
            return
        await self.session.execute(delete(RolePermission).where(RolePermission.role_id == rid))
        if permission_ids:
            await self.grant_permissions_to_role(role_id, permission_ids, assigned_by)
        logger.info("Set %s permissions for role %s", len(permission_ids), role_id)

    async def revoke_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        rid = BaseRepository.parse_id(role_id)
        pid = BaseRepository.parse_id(permission_id)
        if not rid or not pid:
            return False
        result = await self.session.execute(
            delete(RolePermission).where(
                RolePermission.role_id == rid,
                RolePermission.permission_id == pid,
            )
        )
        return (result.rowcount or 0) > 0

    async def get_role_permissions(self, role_id: str) -> List[PermissionResponse]:
        uid = BaseRepository.parse_id(role_id)
        if not uid:
            return []
        result = await self.session.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == uid)
        )
        return [self._perm_response(p) for p in result.scalars().all()]

    # ==================== USER-ROLE ASSIGNMENT ====================

    async def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        assigned_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ):
        uid = BaseRepository.parse_id(user_id)
        rid = BaseRepository.parse_id(role_id)
        if not uid or not rid:
            return
        assigned_by_id = BaseRepository.parse_id(assigned_by) if assigned_by else None
        stmt = (
            pg_insert(UserRole)
            .values(
                user_id=uid,
                role_id=rid,
                assigned_at=datetime.utcnow(),
                assigned_by=assigned_by_id,
                expires_at=expires_at,
            )
            .on_conflict_do_update(
                index_elements=["user_id", "role_id"],
                set_={
                    "assigned_at": datetime.utcnow(),
                    "assigned_by": assigned_by_id,
                    "expires_at": expires_at,
                },
            )
        )
        await self.session.execute(stmt)
        role = await self.session.get(Role, rid)
        user = await self.session.get(User, uid)
        if role and user:
            user.role = role.code
            user.updated_at = datetime.utcnow()
        logger.info("Assigned role %s to user %s", role_id, user_id)

    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        uid = BaseRepository.parse_id(user_id)
        rid = BaseRepository.parse_id(role_id)
        if not uid or not rid:
            return False
        result = await self.session.execute(
            delete(UserRole).where(UserRole.user_id == uid, UserRole.role_id == rid)
        )
        if (result.rowcount or 0) == 0:
            return False
        remaining = await self.get_user_roles(user_id)
        user = await self.session.get(User, uid)
        if user:
            user.role = remaining[0].code if remaining else "student"
            user.updated_at = datetime.utcnow()
        return True

    async def get_user_roles(self, user_id: str) -> List[RoleResponse]:
        uid = BaseRepository.parse_id(user_id)
        if not uid:
            return []
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == uid,
                Role.is_active.is_(True),
                or_(UserRole.expires_at.is_(None), UserRole.expires_at > now),
            )
        )
        roles = result.scalars().all()
        out = []
        for role in roles:
            out.append(self._role_response(role, await self._perm_count(role.id)))
        return out

    async def get_user_permissions(self, user_id: str) -> List[PermissionResponse]:
        uid = BaseRepository.parse_id(user_id)
        if not uid:
            return []
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .join(Role, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == uid,
                Role.is_active.is_(True),
                or_(UserRole.expires_at.is_(None), UserRole.expires_at > now),
            )
            .distinct()
        )
        return [self._perm_response(p) for p in result.scalars().all()]
