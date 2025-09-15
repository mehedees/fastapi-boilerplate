from dataclasses import asdict

from sqlalchemy import select

from app.domain.users.entities import UserCreateEntity, UserEntity
from app.infra.persistence.models.user import UserModel

from .base import BaseRepoImpl


class UserRepoImpl(BaseRepoImpl):
    def __init__(self, **kwargs):
        super().__init__(model=UserModel, **kwargs)

    async def create_user(self, user: UserCreateEntity) -> UserEntity:
        with self.session_factory() as session:
            obj = self.__model(**asdict(user))
            session.add(obj)
            session.flush()
            print("after flush: ", obj)
            session.refresh(obj)
            print("after refresh: ", obj)

        return obj.to_dataclass(UserEntity)

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        with self.session_factory(read_only=True) as session:
            stmt = select(UserModel).filter_by(email=email)
            result = session.execute(stmt).scalars().one_or_none()
            return result.to_dataclass(UserEntity) if result else None
