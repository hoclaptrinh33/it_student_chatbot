"""
API Dependencies - Dependency injection cho FastAPI với RBAC
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.jwt_service import JWTService
from app.models.user import UserInDB, UserRole, Permission
from typing import Annotated, List, Callable

# Security scheme
security = HTTPBearer()


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    return AuthService(user_repo)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserInDB:
    token = credentials.credentials

    token_data = auth_service.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


def require_permission(permission: str) -> Callable:
    async def check_permission(
        current_user: Annotated[UserInDB, Depends(get_current_user)],
        rbac_service: Annotated["RBACService", Depends(get_rbac_service)]
    ) -> UserInDB:
        if current_user.role == "admin":
             return current_user

        has_perm = await rbac_service.check_permission(
            user_id=current_user.id,
            permission_code=permission
        )

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user
    return check_permission


def require_role(allowed_roles: List[UserRole]) -> Callable:
    async def check_role(
        current_user: Annotated[UserInDB, Depends(get_current_user)]
    ) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role.value} not authorized"
            )
        return current_user
    return check_role


async def get_admin_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserInDB:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_teacher_or_admin(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserInDB:
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or Admin access required"
        )
    return current_user


def get_rbac_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> "RBACRepository":
    from app.repositories.rbac_repository import RBACRepository
    return RBACRepository(session)


def get_rbac_service(
    rbac_repo: Annotated["RBACRepository", Depends(get_rbac_repository)]
) -> "RBACService":
    from app.services.rbac_service import RBACService
    return RBACService(rbac_repo)
