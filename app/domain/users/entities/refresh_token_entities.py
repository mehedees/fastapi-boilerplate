from dataclasses import dataclass
from datetime import datetime


@dataclass
class RefreshTokenEntity:
    id: int
    user_id: int
    device_info: str
    created_at: datetime
    expires_at: datetime


@dataclass
class RefreshTokenCreateEntity:
    user_id: int
    device_info: str
    expires_at: datetime


@dataclass
class RefreshTokenPayloadEntity:
    user_id: int
    email: str
    refresh_token_id: int
    iat: datetime
    exp: datetime
    token_type: str
