"""UUID parse_id + seed login (sv01 / Pass123) without live Postgres."""
from uuid import UUID

import pytest

from app.repositories.base_repository import BaseRepository
from app.services.auth_service import AuthService

SEED_HASH = "$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0"
SEED_USER = {
    "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
    "email": "sv01@fit.edu.vn",
    "hashed_password": SEED_HASH,
    "full_name": "Lê Hải Đăng",
    "role": "student",
    "is_active": True,
    "student_code": "SV001",
    "department": "Khoa CNTT",
    "created_at": None,
}


def test_parse_id_accepts_uuid():
    uid = BaseRepository.parse_id("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
    assert uid == UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")


def test_parse_id_rejects_mongo_objectid():
    assert BaseRepository.parse_id("507f1f77bcf86cd799439011") is None
    assert BaseRepository.parse_id("not-a-uuid") is None
    assert BaseRepository.parse_id(None) is None


def test_serialize_row_uuid_to_str():
    class Row:
        __table__ = type("T", (), {"columns": []})
        def __init__(self):
            self.id = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
            self.email = "sv01@fit.edu.vn"

    # no __table__.columns walk — use dict path
    doc = BaseRepository.serialize_row({
        "id": UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        "email": "sv01@fit.edu.vn",
    })
    assert doc["id"] == "cccccccc-cccc-cccc-cccc-cccccccccccc"
    assert isinstance(doc["id"], str)


class FakeUserRepo:
    async def get_by_email(self, email):
        if email == SEED_USER["email"]:
            return dict(SEED_USER)
        return None

    async def get_role_code(self, user_id):
        if user_id == SEED_USER["id"]:
            return "student"
        return None

    async def get_by_id(self, user_id):
        if user_id == SEED_USER["id"]:
            from datetime import datetime
            doc = dict(SEED_USER)
            doc["created_at"] = datetime.utcnow()
            return doc
        return None


@pytest.mark.asyncio
async def test_login_seed_sv01():
    from datetime import datetime
    SEED_USER["created_at"] = datetime.utcnow()
    svc = AuthService(FakeUserRepo())
    token = await svc.login("sv01@fit.edu.vn", "Pass123")
    assert token.access_token
    data = svc.verify_token(token.access_token)
    assert data.user_id == SEED_USER["id"]
    assert data.email == "sv01@fit.edu.vn"
    assert data.role == "student"


@pytest.mark.asyncio
async def test_login_seed_sv01_wrong_password():
    from datetime import datetime
    SEED_USER["created_at"] = datetime.utcnow()
    svc = AuthService(FakeUserRepo())
    with pytest.raises(ValueError):
        await svc.login("sv01@fit.edu.vn", "WrongPass")
