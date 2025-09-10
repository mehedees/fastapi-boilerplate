from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from app.core.container import Container
from app.domain.users.services import UserService


class UserViews:
    @staticmethod
    @inject
    async def create_user(
        user_service: UserService = Depends(Provide[Container.user_service]),
    ):
        pass
