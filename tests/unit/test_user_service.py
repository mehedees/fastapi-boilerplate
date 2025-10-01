from datetime import datetime

import pytest

from app.domain.users.entities import (
    LoginRequestEntity,
    UserCreateEntity,
    UserCredentialsEntity,
    UserEntity,
)
from app.domain.users.exceptions import InvalidPasswordException, UserNotFoundException
from app.domain.users.services import UserService


class FakeRepo:
    def __init__(self, creds=None, user=None):
        self._creds = creds
        self._user = user

    async def create_user(self, user: UserCreateEntity) -> UserEntity:
        return UserEntity(
            id=1,
            email=user.email,
            name=user.name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def get_user_by_email(self, email: str):
        return None

    async def get_user_by_id(self, user_id: int):
        if self._user is None:
            from app.domain.users.exceptions import UserNotFoundException

            raise UserNotFoundException
        return self._user

    async def get_user_creds_by_email(self, email: str):
        return self._creds

    async def list_users(self, limit, offset):
        return ()


class FakeHash:
    def __init__(self, ok=True):
        self.ok = ok

    def verify_password_argon2(self, p, h):
        return self.ok

    def hash_password_argon2(self, p):
        return "hashed"


class FakeTokens:
    def generate_token(self, payload, token_type, expiry_sec):
        return f"{token_type}-token", 0


class FakeSettings:
    ACCESS_TOKEN_EXPIRE_SECONDS = 3600
    REFRESH_TOKEN_EXPIRE_SECONDS = 7200


@pytest.mark.asyncio
async def test_login_user_not_found():
    service = UserService(
        FakeSettings(), FakeRepo(creds=None), FakeHash(), FakeTokens()
    )
    with pytest.raises(UserNotFoundException):
        await service.login(LoginRequestEntity(email="a@b.com", password="x"))


@pytest.mark.asyncio
async def test_login_invalid_password():
    creds = UserCredentialsEntity(
        id=1,
        email="a@b.com",
        name="A",
        password="hashed",
        created_at=None,
        updated_at=None,
    )
    service = UserService(
        FakeSettings(), FakeRepo(creds=creds), FakeHash(ok=False), FakeTokens()
    )
    with pytest.raises(InvalidPasswordException):
        await service.login(LoginRequestEntity(email="a@b.com", password="x"))


@pytest.mark.asyncio
async def test_login_success():
    creds = UserCredentialsEntity(
        id=1,
        email="a@b.com",
        name="A",
        password="hashed",
        created_at=None,
        updated_at=None,
    )
    service = UserService(
        FakeSettings(), FakeRepo(creds=creds), FakeHash(ok=True), FakeTokens()
    )
    out = await service.login(LoginRequestEntity(email="a@b.com", password="x"))
    assert out.tokens.access_token == "access-token"
    assert out.tokens.refresh_token == "refresh-token"
    assert out.user.email == "a@b.com"
