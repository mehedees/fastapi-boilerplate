from app.core.settings import Settings
from app.core.utils.auth import SecureHashManager
from app.core.utils.token import TokenUtils
from app.domain.users.entities import (
    LoginRequestEntity,
    LoginResponseEntity,
    LoginTokenEntity,
    UserCreateEntity,
    UserCredentialsEntity,
    UserEntity,
)
from app.domain.users.exceptions import (
    InvalidPasswordException,
    UserAlreadyExist,
    UserNotFoundException,
)
from app.domain.users.repo import UserRepo


class UserService:
    def __init__(
        self,
        settings: Settings,
        repo: UserRepo,
        hash_manager: SecureHashManager,
        token_util: TokenUtils,
    ) -> None:
        self.__settings = settings
        self.__repo = repo
        self.__hash_manager = hash_manager
        self.__token_util = token_util

    async def create_user(self, user: UserCreateEntity) -> UserEntity:
        # check if the user already exists
        existing_user: UserEntity | None = await self.__repo.get_user_by_email(
            user.email
        )
        if existing_user:
            raise UserAlreadyExist("User already exists")

        # hash password
        user.password = self.__hash_manager.hash_password_argon2(user.password)

        new_user: UserEntity = await self.__repo.create_user(user)

        return new_user

    async def list_users(
        self, limit: int | None = None, offset: int | None = None
    ) -> tuple[UserEntity]:
        return await self.__repo.list_users(limit, offset)

    async def login(self, login_req_payload: LoginRequestEntity) -> LoginResponseEntity:
        # fetch user if exists
        user_creds: (
            UserCredentialsEntity | None
        ) = await self.__repo.get_user_creds_by_email(login_req_payload.email)
        if user_creds is None:
            raise UserNotFoundException

        # match password
        if not self.__hash_manager.verify_password_argon2(
            login_req_payload.password, user_creds.password
        ):
            raise InvalidPasswordException

        # generate token
        token_payload = {"user_id": user_creds.id}
        access_token, access_token_iat = self.__token_util.generate_token(
            token_payload,
            token_type="access",
            expiry_sec=self.__settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        )
        refresh_token, refresh_token_iat = self.__token_util.generate_token(
            token_payload,
            token_type="refresh",
            expiry_sec=self.__settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )
        return LoginResponseEntity(
            tokens=LoginTokenEntity(
                access_token=access_token,
                access_token_iat=access_token_iat,
                access_token_exp_seconds=self.__settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                refresh_token=refresh_token,
                refresh_token_iat=refresh_token_iat,
                refresh_token_exp_seconds=self.__settings.REFRESH_TOKEN_EXPIRE_SECONDS,
                token_type="Bearer",
            ),
            user=UserEntity(
                id=user_creds.id,
                email=user_creds.email,
                name=user_creds.name,
                created_at=user_creds.created_at,
                updated_at=user_creds.updated_at,
            ),
        )
