from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from app.api.v1.users.schema import UserLoginRequest
from app.core.container import Container
from app.domain.users.services import UserService


class UserViews:
    @staticmethod
    @inject
    async def login(
        payload: UserLoginRequest,
        user_service: UserService = Depends(Provide[Container.user_service]),
    ):
        pass
