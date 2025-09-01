from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    email: str
    name: str
    password: str

    created_at: datetime
    updated_at: datetime


@dataclass
class UserCreate:
    email: str
    name: str
    password: str


@dataclass
class UserUpdate:
    email: str | None = None
    name: str | None = None
    password: str | None = None
