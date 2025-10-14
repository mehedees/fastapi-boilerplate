from datetime import datetime

import pytest

from app.domain.users.entities.refresh_token_entities import (
    RefreshTokenEntity,
)
from app.domain.users.entities.user_entities import (
    LoginRequestEntity,
    UserCreateEntity,
    UserCredentialsEntity,
    UserEntity,
)
from app.domain.users.exceptions import (
    InvalidPasswordException,
    UserNotFoundException,
)
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
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    async def get_user_by_email(self, email: str):
        return None

    async def get_user_by_id(self, user_id: int):
        if self._user is None:
            from app.domain.users.exceptions import (
                UserNotFoundException,
            )

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
    def generate_access_token(self, payload, expiry_sec):
        return "access-token", 0

    def generate_refresh_token(self, payload, expiry_sec):
        return "refresh-token", 0


class FakeSettings:
    ACCESS_TOKEN_EXPIRE_SECONDS = 3600
    REFRESH_TOKEN_EXPIRE_SECONDS = 7200


class FakeUserAgentUtil:
    def parse_user_agent(self, ua_string: str):
        return {"browser": "x", "os": "y", "device": "z"}


class FakeRefreshTokenRepo:
    def __init__(self):
        self.data = RefreshTokenEntity(
            id=1,
            user_id=1,
            device_info="x",
            created_at=datetime.now(),
            expires_at=datetime.now(),
        )

    async def create_refresh_token(self, data: dict):
        return self.data

    async def get_refresh_token_by_id(self, refresh_token_id: int):
        return self.data

    async def delete_refresh_token_by_id(self, refresh_token_id: int):
        return None

    async def delete_refresh_token_by_user_id(self, user_id: int):
        return 1

    async def delete_refresh_token_by_user_id_device_info(
        self, user_id: int, device_info: str
    ):
        return 1


@pytest.mark.asyncio
async def test_login_user_not_found():
    service = UserService(
        FakeSettings(),
        FakeRepo(creds=None),
        FakeRefreshTokenRepo(),
        FakeHash(),
        FakeTokens(),
        FakeUserAgentUtil(),
    )
    with pytest.raises(UserNotFoundException):
        await service.login(
            LoginRequestEntity(email="a@b.com", password="x"),
            user_agent="x",
        )


@pytest.mark.asyncio
async def test_login_invalid_password():
    creds = UserCredentialsEntity(
        id=1,
        email="a@b.com",
        name="A",
        password="hashed",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    service = UserService(
        FakeSettings(),
        FakeRepo(creds=creds),
        FakeRefreshTokenRepo(),
        FakeHash(ok=False),
        FakeTokens(),
        FakeUserAgentUtil(),
    )
    with pytest.raises(InvalidPasswordException):
        await service.login(
            LoginRequestEntity(email="a@b.com", password="x"),
            user_agent="x",
        )


@pytest.mark.asyncio
async def test_login_success():
    creds = UserCredentialsEntity(
        id=1,
        email="a@b.com",
        name="A",
        password="hashed",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    service = UserService(
        FakeSettings(),
        FakeRepo(creds=creds),
        FakeRefreshTokenRepo(),
        FakeHash(ok=True),
        FakeTokens(),
        FakeUserAgentUtil(),
    )
    out = await service.login(
        LoginRequestEntity(email="a@b.com", password="x"),
        user_agent="x",
    )
    assert out.access_token == "access-token"
