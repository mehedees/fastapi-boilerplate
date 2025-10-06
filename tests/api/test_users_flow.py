from datetime import datetime

import pytest
from dependency_injector import providers
from httpx import ASGITransport, AsyncClient

from app.core.app import create_fastapi_app
from app.domain.users.entities.refresh_token_entities import RefreshTokenEntity


class InMemoryUserRepo:
    def __init__(self):
        self._users = {}
        self._creds_by_email = {}

    async def create_user(self, user):
        self._users[user.email] = user
        return user

    async def get_user_by_email(self, email):
        return self._users.get(email)

    async def get_user_by_id(self, user_id: int):
        for u in self._users.values():
            if u.id == user_id:
                return u
        from app.domain.users.exceptions import UserNotFoundException

        raise UserNotFoundException

    async def get_user_creds_by_email(self, email):
        return self._creds_by_email.get(email)

    async def list_users(self, limit, offset):
        return tuple(self._users.values())


class FakeRefreshTokenRepo:
    def __init__(self):
        self.data = RefreshTokenEntity(
            id=1,
            user_id=1,
            device_info="browser:x||os:y||device:z",
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

    async def delete_refresh_token_by_user_id_device_info(self, user_id: int, device_info: str):
        return 1


class FakeUserAgentUtil:
    def parse_user_agent(self, ua_string: str):
        return {"browser": "x", "os": "y", "device": "z"}


@pytest.mark.asyncio
async def test_login_and_me_flow(monkeypatch):
    app = create_fastapi_app()
    container = app.container

    fake_repo = InMemoryUserRepo()
    fake_refresh_token_repo = FakeRefreshTokenRepo()
    container.user_repository.override(providers.Object(fake_repo))
    container.refresh_token_repository.override(providers.Object(fake_refresh_token_repo))

    # Seed creds expected by login
    from app.domain.users.entities.user_entities import UserCredentialsEntity, UserEntity

    now = datetime.now()
    fake_repo._creds_by_email["a@b.com"] = UserCredentialsEntity(
        id=1,
        email="a@b.com",
        name="A",
        is_active=True,
        password="hashed",
        created_at=now,
        updated_at=now,
    )
    fake_repo._users["a@b.com"] = UserEntity(
        id=1, email="a@b.com", name="A", is_active=True, created_at=now, updated_at=now
    )

    # Make password verify always succeed for simplicity
    from app.core.utils import auth as auth_utils

    monkeypatch.setattr(
        auth_utils.SecureHashManager, "verify_password_argon2", lambda *a, **k: True
    )

    transport = ASGITransport(app=app)  # ensures startup/shutdown run
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(
            "/api/v1/users/login", data={"username": "a@b.com", "password": "x"}
        )
        assert r.status_code == 200
        access = r.json()["access_token"]

        r2 = await ac.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {access}"}
        )
        assert r2.status_code == 200

@pytest.mark.asyncio
async def test_refresh_token_flow(monkeypatch):
    app = create_fastapi_app()
    container = app.container

    fake_repo = InMemoryUserRepo()
    fake_refresh_token_repo = FakeRefreshTokenRepo()
    fake_user_agent_util = FakeUserAgentUtil()
    container.user_repository.override(providers.Object(fake_repo))
    container.refresh_token_repository.override(providers.Object(fake_refresh_token_repo))
    container.user_agent_util.override(providers.Object(fake_user_agent_util))

    # Seed creds expected by login
    from app.domain.users.entities.user_entities import UserCredentialsEntity, UserEntity

    now = datetime.now()
    fake_repo._creds_by_email["a@b.com"] = UserCredentialsEntity(
        id=1,
        email="a@b.com",
        name="A",
        is_active=True,
        password="hashed",
        created_at=now,
        updated_at=now,
    )
    fake_repo._users["a@b.com"] = UserEntity(
        id=1, email="a@b.com", name="A", is_active=True, created_at=now, updated_at=now
    )

    # Make password verify always succeed for simplicity
    from app.core.utils import auth as auth_utils

    monkeypatch.setattr(
        auth_utils.SecureHashManager, "verify_password_argon2", lambda *a, **k: True
    )

    transport = ASGITransport(app=app)  # ensures startup/shutdown run
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(
            "/api/v1/users/login", data={"username": "a@b.com", "password": "x"}
        )
        refresh_token = r.cookies["refresh_token"]
        assert r.status_code == 200

        r2 = await ac.post(
            "/api/v1/users/refresh-token", cookies={"refresh_token": refresh_token}
        )
        assert r2.status_code == 200