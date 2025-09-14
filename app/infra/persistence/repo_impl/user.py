from dataclasses import asdict

from app.domain.users.entities import UserCreateEntity, UserEntity
from app.infra.persistence.models.user import UserModel

from .base import BaseRepoImpl


class UserRepoImpl(BaseRepoImpl):
    def __init__(self, **kwargs):
        super().__init__(model=UserModel, **kwargs)

    def create_user(self, user: UserCreateEntity) -> UserEntity:
        obj = self.__model(**asdict(user))
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)

        return obj.to_dataclass(UserEntity)
