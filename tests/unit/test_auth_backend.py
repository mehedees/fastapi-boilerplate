import jwt
import pytest
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from app.core.middlewares.auth import AuthError, AuthErrorType, JWTAuthBackend


class DummyHTTPBearer:
    async def __call__(self, request):
        # Emulate FastAPI’s HTTPBearer returning credentials
        return HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=request.state.token
        )


class DummyTokenUtils:
    def __init__(self, payload_or_exc):
        self.payload_or_exc = payload_or_exc

    def decode_token(self, token):
        if isinstance(self.payload_or_exc, Exception):
            raise self.payload_or_exc
        return self.payload_or_exc


@pytest.mark.asyncio
async def test_auth_backend_success(monkeypatch):
    backend = JWTAuthBackend(
        access_token_secret_key="k", refresh_token_secret_key="k", algorithm="HS256"
    )
    # Patch private members for testability
    # TODO try without patching, using DI to provide tokenutil and httpbearer
    monkeypatch.setattr(backend, "_JWTAuthBackend__http_bearer", DummyHTTPBearer())
    monkeypatch.setattr(
        backend,
        "_JWTAuthBackend__token_util",
        DummyTokenUtils({"user_id": 1, "email": "a@b.com", "token_type": "access"}),
    )

    scope = {"type": "http"}
    request = Request(scope)
    request.state.token = "any"

    creds = await backend.authenticate(request)
    assert creds[0].scopes == ["authenticated"]
    user = creds[1]
    assert user.is_authenticated
    assert user.identity == "1"


@pytest.mark.asyncio
async def test_auth_backend_expired_token(monkeypatch):
    backend = JWTAuthBackend(
        access_token_secret_key="k", refresh_token_secret_key="k", algorithm="HS256"
    )
    monkeypatch.setattr(backend, "_JWTAuthBackend__http_bearer", DummyHTTPBearer())
    monkeypatch.setattr(
        backend,
        "_JWTAuthBackend__token_util",
        DummyTokenUtils(jwt.ExpiredSignatureError()),
    )

    request = Request({"type": "http"})
    request.state.token = "expired"
    with pytest.raises(AuthError) as ei:
        await backend.authenticate(request)
    assert ei.value.err_type == AuthErrorType.TOKEN_EXPIRED
