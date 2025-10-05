import pytest
from starlette.types import Scope

from app.core.middlewares.auth import AuthMiddleware, JWTAuthBackend


class PassThroughApp:
    def __init__(self):
        self.called = False

    async def __call__(self, scope, receive, send):
        self.called = True


@pytest.mark.asyncio
async def test_excluded_path_skips_auth():
    app = PassThroughApp()
    am = AuthMiddleware(
        app,
        backend=JWTAuthBackend("k", "k", "HS256"),
        exclude_paths=["/health", "/users/login"],
    )

    scope: Scope = {"type": "http", "path": "/health"}

    async def dummy_recv():
        pass

    async def dummy_send(msg):
        pass

    await am(scope, dummy_recv, dummy_send)
    assert app.called is True
