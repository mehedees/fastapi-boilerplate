from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import (
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
    """
    A collection of static methods for handling user-related API endpoints.
    """

    @staticmethod
    @inject
    async def login(
        request: Request,
        response: Response,
        settings: Settings = Depends(Provide[Container.settings]),  # noqa: B008
        payload: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
        user_service: UserService = Depends(
            Provide[Container.user_service]
        ),  # noqa: B008
    ) -> LoginToken:
        """
        Handles user login.

        Args:
            request (Request): The HTTP request object.
            response (Response): The HTTP response object.
            settings (Settings): Application settings, injected via dependency.
            payload (OAuth2PasswordRequestForm): Login credentials (username and password).
            user_service (UserService): Service for user-related operations, injected via dependency.

        Returns:
            LoginToken: Access and refresh tokens for the authenticated user.

        Raises:
            APIException: If the login credentials are invalid.
        """
        try:
            user_agent: str = request.headers.get(
                "user-agent", "unknown"
            )
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
                secure=True
                if settings.ENVIRONMENT == EnvironmentEnum.PROD
                else False,
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
        user_service: UserService = Depends(
            Provide[Container.user_service]
        ),  # noqa: B008
    ) -> APIResponse[UserProfile]:
        """
        Retrieves the profile of the currently authenticated user.

        Args:
            request (Request): The HTTP request object.
            user_service (UserService): Service for user-related operations, injected via dependency.

        Returns:
            APIResponse[UserProfile]: The user's profile data.

        Raises:
            APIException: If the user is not found.
        """
        auth_user = request.user
        try:
            user: UserEntity = await user_service.get_user_by_id(
                auth_user.user_id
            )
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
        user_service: UserService = Depends(
            Provide[Container.user_service]
        ),  # noqa: B008
    ):
        """
        Refreshes the user's authentication tokens.

        Args:
            request (Request): The HTTP request object.
            response (Response): The HTTP response object.
            refresh_token (str): The refresh token from the cookie.
            settings (Settings): Application settings, injected via dependency.
            user_service (UserService): Service for user-related operations, injected via dependency.

        Returns:
            LoginToken: New access and refresh tokens.

        Raises:
            APIException: If the user is inactive or the token is invalid.
        """
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
                secure=True
                if settings.ENVIRONMENT == EnvironmentEnum.PROD
                else False,
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

    @staticmethod
    @inject
    async def logout(
        request: Request,
        response: Response,
        settings: Settings = Depends(Provide[Container.settings]),  # noqa: B008
        user_service: UserService = Depends(
            Provide[Container.user_service]
        ),  # noqa: B008
    ):
        """
        Logs out the currently authenticated user.

        Args:
            request (Request): The HTTP request object.
            response (Response): The HTTP response object.
            settings (Settings): Application settings, injected via dependency.
            user_service (UserService): Service for user-related operations, injected via dependency.

        Returns:
            APIResponse: A message indicating successful logout.

        Raises:
            APIException: If no or invalid token is provided.
        """
        user_agent: str = request.headers.get("user-agent", "unknown")

        http_bearer = HTTPBearer()
        try:
            auth_creds: HTTPAuthorizationCredentials = (
                await http_bearer(request)
            )
        except HTTPException:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No/invalid token provided",
            ) from None

        await user_service.logout(auth_creds.credentials, user_agent)
        response.delete_cookie(
            key=settings.REFRESH_TOKEN_COOKIE_NAME,
            path=settings.AUTH_TOKEN_REFRESH_PATH,
            samesite="strict",
            secure=True
            if settings.ENVIRONMENT == EnvironmentEnum.PROD
            else False,
            httponly=True,
        )
        return APIResponse(message="Logout successful")
