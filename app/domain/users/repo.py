from typing import Protocol

from app.domain.users.entities import User


class UserRepo(Protocol):
    async def get_user_by_email(self, email: str) -> User:
        ...
