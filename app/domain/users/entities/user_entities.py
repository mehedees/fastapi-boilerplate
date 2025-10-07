from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserEntity:
    id: int
    email: str
    name: str
    is_active: bool

    created_at: datetime
    updated_at: datetime


@dataclass
class UserCredentialsEntity:
    id: int
    email: str
    name: str
    is_active: bool
    password: str

    created_at: datetime
    updated_at: datetime


@dataclass
class UserCreateEntity:
    email: str
    name: str
    password: str


@dataclass
class UserUpdateEntity:
    email: str | None = None
    name: str | None = None
    password: str | None = None
    is_active: bool | None = None


@dataclass
class LoginRequestEntity:
    email: str
    password: str


@dataclass
class LoginTokenEntity:
    access_token: str
    access_token_iat: datetime
    access_token_exp_seconds: int
    refresh_token: str
    refresh_token_iat: datetime
    refresh_token_exp_seconds: int
    token_type: str
