from typing import Protocol

from app.domain.users.entities import (
    UserCreateEntity,
    UserCredentialsEntity,
    UserEntity,
)


class UserRepo(Protocol):
    async def create_user(self, user: UserCreateEntity) -> UserEntity: ...

    async def get_user_by_email(self, email: str) -> UserEntity: ...

    async def get_user_creds_by_email(self, email: str) -> UserCredentialsEntity: ...

    async def list_users(
        self, limit: int | None, offset: int | None
    ) -> tuple[UserEntity]: ...
