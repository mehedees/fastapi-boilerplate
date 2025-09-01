from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserEntity:
    id: int
    email: str
    name: str
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
