"""
Password reset tokens stored as SHA-256 hashes in password_reset_tokens.
"""
import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, update

from app.core.settings import settings
from app.models.orm import PasswordResetToken
from app.repositories.base_repository import BaseRepository
from app.services.email_service import send_password_reset_email

logger = logging.getLogger(__name__)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class PasswordResetService:
    def __init__(self, session, user_repo, hash_password):
        self.session = session
        self.user_repo = user_repo
        self.hash_password = hash_password

    async def request_reset(self, email: str) -> None:
        """Always succeeds from the caller's perspective (no email enumeration)."""
        user = await self.user_repo.get_by_email(email.strip().lower())
        if not user:
            logger.info("[RESET] Request for unknown email ignored")
            return

        uid = BaseRepository.parse_id(user["id"])
        if not uid:
            logger.warning("[RESET] User id is not a UUID: %s", user["id"])
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = _hash_token(raw_token)
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=settings.password_reset_expire_minutes)

        await self.session.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == uid,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
        self.session.add(
            PasswordResetToken(
                user_id=uid,
                token_hash=token_hash,
                created_at=now,
                expires_at=expires_at,
                used_at=None,
            )
        )
        await self.session.flush()

        reset_url = f"{settings.frontend_url.rstrip('/')}/auth/reset-password?token={raw_token}"
        try:
            send_password_reset_email(user["email"], reset_url)
        except Exception:
            logger.exception("[RESET] Email send failed; token still issued")
        logger.info("[RESET] Token issued for user_id=%s expires=%s", user["id"], expires_at)

    async def reset_password(self, raw_token: str, new_password: str) -> bool:
        token_hash = _hash_token(raw_token)
        now = datetime.utcnow()
        result = await self.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return False

        hashed = self.hash_password(new_password)
        updated = await self.user_repo.update_user(str(row.user_id), {"hashed_password": hashed})
        if not updated:
            return False

        row.used_at = now
        await self.session.flush()
        return True
