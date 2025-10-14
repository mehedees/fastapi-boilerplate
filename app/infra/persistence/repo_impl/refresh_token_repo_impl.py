from dataclasses import asdict

from sqlalchemy import delete, select
from sqlalchemy.exc import NoResultFound

from app.core.exceptions import NotFoundException
from app.domain.users.entities.refresh_token_entities import (
    RefreshTokenCreateEntity,
    RefreshTokenEntity,
)
from app.infra.persistence.models.refresh_token import RefreshTokenModel

from .base import BaseRepoImpl


class RefreshTokenRepoImpl(BaseRepoImpl):
    def __init__(self, **kwargs):
        super().__init__(model=RefreshTokenModel, **kwargs)

    async def create_refresh_token(
        self, refresh_token: RefreshTokenCreateEntity
    ) -> RefreshTokenEntity:
        with self.session_factory() as session:
            obj = RefreshTokenModel(**asdict(refresh_token))
            session.add(obj)
            session.flush()
            session.refresh(obj)

        return obj.to_dataclass(RefreshTokenEntity)

    async def get_refresh_token_by_id(
        self, refresh_token_id: int
    ) -> RefreshTokenEntity:
        try:
            with self.session_factory(read_only=True) as session:
                stmt = select(RefreshTokenModel).filter_by(
                    id=refresh_token_id
                )
                result = session.scalars(stmt).one()
        except NoResultFound:
            raise NotFoundException from None

        return result.to_dataclass(RefreshTokenEntity)

    async def list_refresh_token_by_user_id(
        self, user_id: int
    ) -> tuple[RefreshTokenEntity, ...]:
        with self.session_factory(read_only=True) as session:
            stmt = select(RefreshTokenModel).filter_by(user_id=user_id)
            result = session.scalars(stmt).all()
        return tuple(
            result.to_dataclass(RefreshTokenEntity) for result in result
        )

    async def retrieve_refresh_token_by_device_info(
        self, device_info: str
    ) -> RefreshTokenEntity | None:
        with self.session_factory(read_only=True) as session:
            stmt = select(RefreshTokenModel).filter_by(
                device_info=device_info
            )
            result = session.scalars(stmt).one_or_none()

        return (
            result.to_dataclass(RefreshTokenEntity) if result else None
        )

    async def delete_refresh_token_by_id(
        self, refresh_token_id: int
    ) -> None:
        with self.session_factory() as session:
            stmt = delete(RefreshTokenModel).filter_by(
                id=refresh_token_id
            )
            session.execute(stmt)

    async def delete_refresh_token_by_user_id(
        self, user_id: int
    ) -> int:
        with self.session_factory() as session:
            stmt = delete(RefreshTokenModel).filter_by(user_id=user_id)
            result = session.execute(stmt)
        return result.rowcount()

    async def delete_refresh_token_by_user_id_device_info(
        self, user_id: int, device_info: str
    ) -> int:
        with self.session_factory() as session:
            stmt = delete(RefreshTokenModel).filter_by(
                user_id=user_id, device_info=device_info
            )
            result = session.execute(stmt)
        return result.rowcount()
