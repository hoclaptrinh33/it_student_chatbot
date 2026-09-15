"""Password reset hashing/expiry unit tests (no SMTP, no Postgres)."""
import hashlib
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from app.services.password_reset_service import _hash_token, PasswordResetService


def test_hash_token_is_sha256():
    token = "abc123"
    assert _hash_token(token) == hashlib.sha256(token.encode()).hexdigest()


class FakeUsers:
    def __init__(self):
        self.users = {
            "cccccccc-cccc-cccc-cccc-cccccccccccc": {
                "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                "email": "sv01@fit.edu.vn",
                "hashed_password": "old",
            }
        }

    async def get_by_email(self, email):
        for user in self.users.values():
            if user["email"] == email:
                return user
        return None

    async def update_user(self, user_id, update_data):
        if user_id not in self.users:
            return False
        self.users[user_id].update(update_data)
        return True


def _session_returning(row):
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = row
    session.execute = AsyncMock(return_value=result)
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_reset_unknown_email_is_silent():
    session = _session_returning(None)
    service = PasswordResetService(session, FakeUsers(), hash_password=lambda p: f"h:{p}")
    await service.request_reset("nobody@fit.edu.vn")
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_reset_password_rejects_bad_token():
    session = _session_returning(None)
    service = PasswordResetService(session, FakeUsers(), hash_password=lambda p: f"h:{p}")
    ok = await service.reset_password("not-a-real-token", "Newpass1!")
    assert ok is False


@pytest.mark.asyncio
async def test_reset_password_accepts_valid_token():
    users = FakeUsers()
    token_row = MagicMock()
    token_row.user_id = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
    token_row.used_at = None
    token_row.expires_at = datetime.utcnow() + timedelta(minutes=10)
    session = _session_returning(token_row)
    service = PasswordResetService(session, users, hash_password=lambda p: f"h:{p}")
    raw = "valid-token-value-123456"
    ok = await service.reset_password(raw, "Newpass1!")
    assert ok is True
    assert users.users["cccccccc-cccc-cccc-cccc-cccccccccccc"]["hashed_password"] == "h:Newpass1!"
    assert token_row.used_at is not None
