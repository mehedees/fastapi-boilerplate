from dataclasses import asdict

from app.domain.users.entities import UserCreateEntity, UserEntity
from app.infra.persistence.models.user import UserModel

from .base import BaseRepoImpl


class UserRepoImpl(BaseRepoImpl):
    def __init__(self, **kwargs):
        super().__init__(model=UserModel, **kwargs)

    async def create_user(self, user: UserCreateEntity) -> UserEntity:
        return await self.create(data=asdict(user), entity_type=UserEntity)

    async def get_user_by_email(self, email: str) -> UserEntity:
        pass
