from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import Cookie, Depends, Request, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.api.v1.users.schema import LoginToken, UserProfile
from app.core.container import Container
from app.core.enums import EnvironmentEnum
from app.core.exceptions import APIException
from app.core.schemas.base import APIResponse
from app.core.settings import Settings
from app.domain.users.entities.user_entities import (
    LoginRequestEntity,
    LoginTokenEntity,
    UserEntity,
)
from app.domain.users.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidPasswordException,
    UserNotFoundException,
)
from app.domain.users.services import UserService


class UserViews:
    @staticmethod
    @inject
    async def login(
        request: Request,
        response: Response,
        settings: Settings = Depends(Provide[Container.settings]),  # noqa: B008
        payload: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
        user_service: UserService = Depends(Provide[Container.user_service]),  # noqa: B008
    ) -> LoginToken:
        try:
            user_agent: str = request.headers.get("user-agent", "unknown")
            login_tokens: LoginTokenEntity = await user_service.login(
                login_req_payload=LoginRequestEntity(
                    email=payload.username, password=payload.password
                ),
                user_agent=user_agent,
            )

            response.set_cookie(
                key=settings.REFRESH_TOKEN_COOKIE_NAME,
                value=login_tokens.refresh_token,
                httponly=True,
                max_age=login_tokens.refresh_token_exp_seconds,
                expires=login_tokens.refresh_token_exp_seconds,
                samesite="strict",
                secure=True if settings.ENVIRONMENT == EnvironmentEnum.PROD else False,
                path=settings.AUTH_TOKEN_REFRESH_PATH,
            )
            return LoginToken(**asdict(login_tokens))
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

    @staticmethod
    @inject
    async def refresh_token(
        request: Request,
        response: Response,
        refresh_token: str = Cookie(),
        settings: Settings = Depends(Provide[Container.settings]),  # noqa: B008
        user_service: UserService = Depends(Provide[Container.user_service]),  # noqa: B008
    ):
        user_agent: str = request.headers.get("user-agent", "unknown")
        try:
            tokens: LoginTokenEntity = await user_service.refresh_token(
                refresh_token, user_agent
            )
            response.set_cookie(
                key=settings.REFRESH_TOKEN_COOKIE_NAME,
                value=tokens.refresh_token,
                httponly=True,
                max_age=tokens.refresh_token_exp_seconds,
                expires=tokens.refresh_token_exp_seconds,
                samesite="strict",
                secure=True if settings.ENVIRONMENT == EnvironmentEnum.PROD else False,
                path=settings.AUTH_TOKEN_REFRESH_PATH,
            )
            return LoginToken(**asdict(tokens))
        except InactiveUserException:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            ) from None
        except InvalidCredentialsException:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from None
