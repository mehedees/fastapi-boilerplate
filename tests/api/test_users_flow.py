from datetime import datetime

import pytest
from dependency_injector import providers
from httpx import ASGITransport, AsyncClient

from app.core.app import create_fastapi_app


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


@pytest.mark.asyncio
async def test_login_and_me_flow(monkeypatch):
    app = create_fastapi_app()
    container = app.container

    fake_repo = InMemoryUserRepo()
    container.user_repository.override(providers.Object(fake_repo))

    # Seed creds expected by login
    from app.domain.users.entities import UserCredentialsEntity, UserEntity

    now = datetime.now()
    fake_repo._creds_by_email["a@b.com"] = UserCredentialsEntity(
        id=1,
        email="a@b.com",
        name="A",
        password="hashed",
        created_at=now,
        updated_at=now,
    )
    fake_repo._users["a@b.com"] = UserEntity(
        id=1, email="a@b.com", name="A", created_at=now, updated_at=now
    )

    # Make password verify always succeed for simplicity
    from app.core.utils import auth as auth_utils

    monkeypatch.setattr(
        auth_utils.SecureHashManager, "verify_password_argon2", lambda *a, **k: True
    )

    transport = ASGITransport(app=app)  # ensures startup/shutdown run
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(
            "/api/v1/users/login", json={"email": "a@b.com", "password": "x"}
        )
        assert r.status_code == 200
        access = r.json()["data"]["tokens"]["access_token"]

        r2 = await ac.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {access}"}
        )
        assert r2.status_code == 200
