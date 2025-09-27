from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, status

from app.api.v1.users.schema import UserLoginRequest, UserLoginResponse
from app.core.container import Container
from app.core.exceptions import APIException
from app.domain.users.entities import LoginRequestEntity, LoginResponseEntity
from app.domain.users.exceptions import InvalidPasswordException, UserNotFoundException
from app.domain.users.services import UserService


class UserViews:
    @staticmethod
    @inject
    async def login(
        payload: UserLoginRequest,
        user_service: UserService = Depends(Provide[Container.user_service]),  # noqa: B008
    ) -> UserLoginResponse:
        try:
            login_response: LoginResponseEntity = await user_service.login(
                login_req_payload=LoginRequestEntity(**payload.model_dump())
            )
            return UserLoginResponse(**asdict(login_response))
        except (UserNotFoundException, InvalidPasswordException):
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials",
            ) from None
