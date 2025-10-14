from typing import Protocol

from sqlalchemy.orm import Session

from app.domain.users.entities.refresh_token_entities import (
    RefreshTokenCreateEntity,
    RefreshTokenEntity,
)


class RefreshTokenRepo(Protocol):
    async def create_refresh_token(
        self,
        refresh_token: RefreshTokenCreateEntity,
        session: Session | None = None,
    ) -> RefreshTokenEntity: ...
    async def get_refresh_token_by_id(
        self, refresh_token_id: int
    ) -> RefreshTokenEntity: ...
    async def list_refresh_token_by_user_id(
        self, user_id: int
    ) -> tuple[RefreshTokenEntity, ...]: ...
    async def retrieve_refresh_token_by_device_info(
        self, device_info: str
    ) -> RefreshTokenEntity | None: ...
    async def delete_refresh_token_by_id(
        self, refresh_token_id: int
    ) -> None: ...
    async def delete_refresh_token_by_user_id(
        self, user_id: int
    ) -> int: ...
    async def delete_refresh_token_by_user_id_device_info(
        self, user_id: int, device_info: str
    ) -> int: ...
