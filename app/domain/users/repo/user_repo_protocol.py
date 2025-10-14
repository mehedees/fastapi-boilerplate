from typing import Protocol

from sqlalchemy.orm import Session

from app.domain.users.entities.user_entities import (
    UserCreateEntity,
    UserCredentialsEntity,
    UserEntity,
)


class UserRepo(Protocol):
    async def create_user(
        self, user: UserCreateEntity, session: Session | None = None
    ) -> UserEntity: ...

    async def get_user_by_email(
        self, email: str, session: Session | None = None
    ) -> UserEntity | None: ...

    async def get_user_by_id(self, user_id: int) -> UserEntity: ...

    async def get_user_creds_by_email(
        self, email: str
    ) -> UserCredentialsEntity | None: ...

    async def list_users(
        self, limit: int | None, offset: int | None
    ) -> tuple[UserEntity, ...]: ...
