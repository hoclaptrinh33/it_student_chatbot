"""
Auth Service - Business logic cho authentication
"""
from passlib.context import CryptContext
from app.repositories.user_repository import UserRepository
from app.services.jwt_service import JWTService
from app.models.user import UserCreate, UserInDB, Token
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    """Service xử lý authentication logic"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.jwt_service = JWTService()

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def register(self, user_data: UserCreate) -> Token:
        if await self.user_repo.email_exists(user_data.email):
            raise ValueError("Email này đã được đăng ký")

        hashed_password = self.hash_password(user_data.password)
        user = await self.user_repo.create_user(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role.value,
            student_code=getattr(user_data, "student_code", None),
        )
        logger.info("User registered: %s", user["email"])

        access_token = self.jwt_service.create_access_token(
            user_id=user["id"],
            email=user["email"],
            role=user["role"],
        )
        return Token(access_token=access_token)

    async def login(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.debug("Login failed: unknown email")
            raise ValueError("Email không tồn tại trong hệ thống")

        is_valid = self.verify_password(password, user["hashed_password"])
        if not is_valid:
            logger.debug("Login failed: password mismatch for user_id=%s", user["id"])
            raise ValueError("Mật khẩu không chính xác")

        if not user.get("is_active", True):
            raise ValueError("Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên.")

        user_role_code = await self._get_user_role(user["id"], fallback=user.get("role"))
        logger.info("User logged in: %s (role: %s)", email, user_role_code)

        access_token = self.jwt_service.create_access_token(
            user_id=user["id"],
            email=user["email"],
            role=user_role_code,
        )
        return Token(access_token=access_token)

    async def _get_user_role(self, user_id: str, fallback: Optional[str] = None) -> str:
        role_code = await self.user_repo.get_role_code(user_id)
        if role_code:
            return role_code
        if fallback:
            return fallback
        logger.warning("User %s has no role assigned, defaulting to 'student'", user_id)
        return "student"

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        user["role"] = await self._get_user_role(user_id, fallback=user.get("role"))
        return UserInDB(**user)

    def verify_token(self, token: str):
        return self.jwt_service.verify_token(token)

    async def get_all_users(self) -> list[UserInDB]:
        users = await self.user_repo.get_all_users()
        result = []
        for user in users:
            try:
                user["role"] = await self._get_user_role(user["id"], fallback=user.get("role"))
            except Exception as e:
                logger.error("Error fetching role for user %s: %s", user.get("id"), e)
                user["role"] = user.get("role") or "student"
            result.append(UserInDB(**user))
        return result

    async def create_user_admin(self, user_data: UserCreate) -> dict:
        if await self.user_repo.email_exists(user_data.email):
            raise ValueError("Email already in use")

        if user_data.role.value == "admin":
            raise ValueError("Không thể tạo user với quyền Admin. Admin là tài khoản duy nhất.")

        hashed_password = self.hash_password(user_data.password)
        user = await self.user_repo.create_user(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role.value,
            student_code=getattr(user_data, "student_code", None),
        )
        logger.info("Assigned role %s to new user %s", user_data.role.value, user["email"])
        return user

    async def update_user_admin(
        self, user_id: str, update_data: dict, replace_roles: bool = True
    ) -> bool:
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = self.hash_password(update_data["password"])
            del update_data["password"]
        if "role" in update_data and hasattr(update_data["role"], "value"):
            update_data["role"] = update_data["role"].value
        return await self.user_repo.update_user(
            user_id, update_data, replace_roles=replace_roles
        )

    async def delete_user_admin(self, user_id: str) -> bool:
        return await self.user_repo.delete_user(user_id)
