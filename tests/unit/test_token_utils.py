from datetime import UTC, datetime

import jwt
from freezegun import freeze_time

from app.core.utils.token import TokenTypeEnum, TokenUtils

SECRET = "test-secret"
ALG = "HS256"


@freeze_time("2025-01-01 00:00:00")
def test_generate_and_decode_token_roundtrip():
    tu = TokenUtils(SECRET, SECRET, ALG)
    token, iat = tu.generate_access_token(
        {"user_id": 1, "email": "a@b.com"}, 3600
    )
    assert isinstance(token, str)
    assert iat == datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

    payload = tu.decode_access_token(token)
    assert payload["user_id"] == 1
    assert payload["email"] == "a@b.com"
    assert payload["token_type"] == TokenTypeEnum.ACCESS


@freeze_time("2025-01-01 00:00:00")
def test_decode_expired_token_raises():
    tu = TokenUtils(SECRET, SECRET, ALG)
    token, _ = tu.generate_access_token({}, 1)
    with freeze_time("2025-01-01 01:00:00"):
        import pytest

        with pytest.raises(jwt.ExpiredSignatureError):
            tu.decode_access_token(token)
