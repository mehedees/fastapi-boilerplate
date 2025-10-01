from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request, status

from app.api.v1.users.schema import UserLoginRequest, UserLoginResponse, UserProfile
from app.core.container import Container
from app.core.exceptions import APIException
from app.core.schemas.base import APIResponse
from app.domain.users.entities import (
    LoginRequestEntity,
    LoginResponseEntity,
    UserEntity,
)
from app.domain.users.exceptions import InvalidPasswordException, UserNotFoundException
from app.domain.users.services import UserService


class UserViews:
    @staticmethod
    @inject
    async def login(
        payload: UserLoginRequest,
        user_service: UserService = Depends(Provide[Container.user_service]),  # noqa: B008
    ) -> APIResponse[UserLoginResponse]:
        try:
            login_response: LoginResponseEntity = await user_service.login(
                login_req_payload=LoginRequestEntity(**payload.model_dump())
            )
            return APIResponse(
                message="Login successful",
                data=UserLoginResponse(**asdict(login_response)),
            )
        except (UserNotFoundException, InvalidPasswordException):
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials",
            ) from None

    @staticmethod
    @inject
    async def me(
        request: Request,
        user_service: UserService = Depends(Provide[Container.user_service]),  # noqa: B008
    ) -> APIResponse[UserProfile]:
        auth_user = request.user
        try:
            user: UserEntity = await user_service.get_user_by_id(auth_user.user_id)
            return APIResponse(
                message="User profile retrieved",
                data=UserProfile(**asdict(user)),
            )
        except UserNotFoundException:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            ) from None
