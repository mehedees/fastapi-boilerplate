from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.domain.users.entities.user_entities import (
    UserCreateEntity,
    UserCredentialsEntity,
    UserEntity,
)
from app.domain.users.exceptions import UserNotFoundException
from app.infra.persistence.models.user import UserModel

from .base import BaseRepoImpl


class UserRepoImpl(BaseRepoImpl):
    def __init__(self, **kwargs):
        super().__init__(model=UserModel, **kwargs)

    async def create_user(
        self, user: UserCreateEntity, session: Session | None = None
    ) -> UserEntity:
        db_session = self._get_session(session)
        should_close = session is None

        try:
            obj = UserModel(**asdict(user))
            db_session.add(obj)
            db_session.flush()
            db_session.refresh(obj)
            return obj.to_dataclass(UserEntity)
        finally:
            if should_close:
                db_session.close()

    async def get_user_by_email(
        self, email: str, session: Session | None = None
    ) -> UserEntity | None:
        db_session = self._get_session(session)
        should_close = session is None

        try:
            stmt = select(UserModel).filter_by(email=email)
            result = db_session.scalars(stmt).one_or_none()
            return result.to_dataclass(UserEntity) if result else None
        finally:
            if should_close:
                db_session.close()

    async def get_user_by_id(self, user_id: int) -> UserEntity:
        """
        Get user by id or raise UserNotFoundException
        :param user_id:
        :return: UserEntity
        """
        try:
            with self.session_factory(read_only=True) as session:
                stmt = select(UserModel).filter_by(id=user_id)
                result = session.scalars(stmt).one()
        except NoResultFound:
            raise UserNotFoundException from None

        return result.to_dataclass(UserEntity)

    async def get_user_creds_by_email(
        self, email: str
    ) -> UserCredentialsEntity | None:
        with self.session_factory(read_only=True) as session:
            stmt = select(UserModel).filter_by(email=email)
            result = session.scalars(stmt).one_or_none()
        return (
            result.to_dataclass(UserCredentialsEntity)
            if result
            else None
        )

    async def list_users(
        self, limit: int | None, offset: int | None
    ) -> tuple[UserEntity, ...]:
        with self.session_factory(read_only=True) as session:
            stmt = select(UserModel).limit(limit).offset(offset)
            result = session.scalars(stmt).all()
        return tuple(
            result.to_dataclass(UserEntity) for result in result
        )
