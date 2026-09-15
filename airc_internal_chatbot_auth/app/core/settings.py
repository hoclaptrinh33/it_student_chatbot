"""
Application Settings - Quản lý environment variables
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


def _reject_mongo_env() -> None:
    if os.getenv("MONGODB_URL") or os.getenv("MONGODB_DB_NAME"):
        raise RuntimeError(
            "MongoDB is no longer supported. Remove MONGODB_URL/MONGODB_DB_NAME and set DATABASE_URL."
        )


_reject_mongo_env()


class Settings(BaseSettings):
    """Application settings từ environment variables"""

    # App config
    app_name: str = "IT Faculty Auth Service"
    debug: bool = False

    # Postgres
    database_url: str = "postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot"

    # JWT configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # Password reset
    frontend_url: str = "http://localhost:3000"
    password_reset_expire_minutes: int = 60

    # SMTP (optional — if unset, reset links are logged only)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None
    smtp_use_tls: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
