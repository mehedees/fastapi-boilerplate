from datetime import datetime, timedelta

import jwt

from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.core.settings import Settings
from app.core.utils.auth import SecureHashManager
from app.core.utils.encoders import safe_jsonable_encoder
from app.core.utils.token import TokenTypeEnum, TokenUtils
from app.core.utils.user_agent import UserAgentUtil
from app.domain.users.entities.refresh_token_entities import (
    RefreshTokenCreateEntity,
    RefreshTokenEntity,
    RefreshTokenPayloadEntity,
)
from app.domain.users.entities.user_entities import (
    LoginRequestEntity,
    LoginTokenEntity,
    UserCreateEntity,
    UserCredentialsEntity,
    UserEntity,
)
from app.domain.users.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidPasswordException,
    SecretLeakException,
    UserAlreadyExist,
    UserNotFoundException,
)
from app.domain.users.repo.refresh_token_repo_protocol import RefreshTokenRepo
from app.domain.users.repo.user_repo_protocol import UserRepo
from app.domain.users.utils import make_device_info_str


class UserService:
    def __init__(
        self,
        settings: Settings,
        repo: UserRepo,
        refresh_token_repo: RefreshTokenRepo,
        hash_manager: SecureHashManager,
        token_util: TokenUtils,
        user_agent_util: UserAgentUtil,
    ) -> None:
        self.__settings = settings
        self.__repo = repo
        self.__refresh_token_repo = refresh_token_repo
        self.__hash_manager = hash_manager
        self.__token_util = token_util
        self.__user_agent_util = user_agent_util

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
    ) -> tuple[UserEntity, ...]:
        return await self.__repo.list_users(limit, offset)

    async def get_user_by_id(self, user_id: int) -> UserEntity:
        user: UserEntity = await self.__repo.get_user_by_id(user_id)
        return user

    async def login(
        self, login_req_payload: LoginRequestEntity, user_agent: str
    ) -> LoginTokenEntity:
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

        # generate access token
        access_token, access_token_iat = self.__make_access_token(
            user_id=user_creds.id,
            email=user_creds.email,
        )

        # clean up same device refresh tokens and generate a new one
        (
            refresh_token,
            refresh_token_iat,
        ) = await self.__cleanup_and_make_same_device_refresh_token(
            user_id=user_creds.id,
            email=user_creds.email,
            device_info=self.__user_agent_util.parse_user_agent(user_agent),
        )
        return LoginTokenEntity(
            access_token=access_token,
            access_token_iat=access_token_iat,
            access_token_exp_seconds=self.__settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            refresh_token=refresh_token,
            refresh_token_iat=refresh_token_iat,
            refresh_token_exp_seconds=self.__settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            token_type="Bearer",
        )

    async def refresh_token(
        self, refresh_token: str, user_agent: str
    ) -> LoginTokenEntity:
        device_info: dict = self.__user_agent_util.parse_user_agent(user_agent)
        device_info_text = make_device_info_str(safe_jsonable_encoder(device_info))

        decoded_refresh_token = await self.__decode_and_validate_refresh_token(
            refresh_token, device_info_text
        )

        # all checks passed, delete the old refresh token
        await self.__refresh_token_repo.delete_refresh_token_by_id(
            decoded_refresh_token.refresh_token_id
        )

        # generate tokens
        access_token, access_token_iat = self.__make_access_token(
            user_id=decoded_refresh_token.user_id,
            email=decoded_refresh_token.email,
        )
        refresh_token, refresh_token_iat = self.__make_refresh_token(
            user_id=decoded_refresh_token.user_id,
            email=decoded_refresh_token.email,
            device_info_text=device_info_text,
        )

        return LoginTokenEntity(
            access_token=access_token,
            access_token_iat=access_token_iat,
            access_token_exp_seconds=self.__settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            refresh_token=refresh_token,
            refresh_token_iat=refresh_token_iat,
            refresh_token_exp_seconds=self.__settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            token_type="Bearer",
        )

    async def __make_access_token(
        self, user_id: int, email: str
    ) -> tuple[str, datetime]:
        access_token_payload = {
            "user_id": user_id,
            "email": email,
        }
        access_token, access_token_iat = self.__token_util.generate_access_token(
            access_token_payload,
            expiry_sec=self.__settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        )
        return access_token, access_token_iat

    async def __make_refresh_token(
        self, user_id: int, email: str, device_info_text: str
    ) -> tuple[str, datetime]:
        db_refresh_token: RefreshTokenEntity = (
            await self.__refresh_token_repo.create_refresh_token(
                RefreshTokenCreateEntity(
                    user_id=user_id,
                    device_info=device_info_text,
                    expires_at=datetime.now()
                    + timedelta(
                        seconds=self.__settings.REFRESH_TOKEN_EXPIRE_SECONDS + 1
                    ),
                    # added leniency so that actual refresh token expiry doesn't lag far behind
                )
            )
        )
        refresh_token_payload = {
            "user_id": user_id,
            "email": email,
            "refresh_token_id": db_refresh_token.id,
        }
        refresh_token, refresh_token_iat = self.__token_util.generate_refresh_token(
            refresh_token_payload,
            expiry_sec=self.__settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )
        return refresh_token, refresh_token_iat

    async def __cleanup_and_make_same_device_refresh_token(
        self, user_id: int, email: str, device_info: dict
    ) -> tuple[str, datetime]:
        device_info_text: str = make_device_info_str(safe_jsonable_encoder(device_info))
        # note: we don't care if a token existed or not, we just delete any existing one for this device
        deleted_tokens: int = (
            await self.__refresh_token_repo.delete_refresh_token_by_user_id_device_info(
                user_id, device_info_text
            )
        )
        if deleted_tokens > 1:
            logger.warning(
                f"Found {deleted_tokens} refresh tokens for user {user_id} and device {device_info_text}"
            )

        return await self.__make_refresh_token(user_id, email, device_info_text)

    async def __handle_expired_refresh_token(self, expired_refresh_token: str):
        # possible replay attack, revoke all user refresh tokens and blacklist user for access token
        expired_refresh_token_payload: dict = self.__token_util.decode_refresh_token(
            expired_refresh_token, verify_expiry=False
        )
        expired_refresh_token = RefreshTokenPayloadEntity(
            **expired_refresh_token_payload
        )
        await self.__revoke_user_tokens(expired_refresh_token.user_id)

    async def __revoke_user_tokens(self, user_id: int):
        deleted_tokens: int = (
            await self.__refresh_token_repo.delete_refresh_token_by_user_id(user_id)
        )
        logger.warning(f"Deleted {deleted_tokens} refresh tokens for user {user_id}")
        # TODO blacklist user for access token

    async def __decode_and_validate_refresh_token(
        self, refresh_token: str, device_info_text: str
    ) -> RefreshTokenPayloadEntity:
        try:
            refresh_token_payload: dict = self.__token_util.decode_refresh_token(
                refresh_token
            )
        except jwt.ExpiredSignatureError:
            await self.__handle_expired_refresh_token(refresh_token)
            raise InvalidCredentialsException(
                "Possible replay attack with expired refresh token."
            ) from None
        except jwt.InvalidTokenError:
            raise InvalidCredentialsException("Invalid refresh token.") from None

        decoded_refresh_token = RefreshTokenPayloadEntity(**refresh_token_payload)

        try:
            # initial checks
            if decoded_refresh_token.token_type != TokenTypeEnum.REFRESH.value:
                raise InvalidCredentialsException(
                    "Possible attack to refresh token with access/other token."
                )

            try:
                db_refresh_token: RefreshTokenEntity = (
                    await self.__refresh_token_repo.get_refresh_token_by_id(
                        decoded_refresh_token.refresh_token_id
                    )
                )
            except NotFoundException:
                raise InvalidCredentialsException(
                    "Refresh token not found. Possible replay attack."
                ) from None

            if db_refresh_token.user_id != decoded_refresh_token.user_id:
                msg = (
                    f"Refresh token user {decoded_refresh_token.user_id} doesn't match db token user {db_refresh_token.user_id}. "
                    f"Possible secret leak. Revoke all tokens of both users and blacklist user for access token."
                )
                raise SecretLeakException(
                    message=msg,
                    user_ids=[decoded_refresh_token.user_id, db_refresh_token.user_id],
                )

            if db_refresh_token.device_info != device_info_text:
                raise InvalidCredentialsException("Trying with other device's token.")

            try:
                user: UserEntity = await self.__repo.get_user_by_id(
                    decoded_refresh_token.user_id
                )
            except UserNotFoundException:
                raise SecretLeakException(
                    message="Token user not found. Possible secret leak.",
                    user_ids=[decoded_refresh_token.user_id],
                ) from None

            # check if the user is active still
            if not user.is_active:
                raise InactiveUserException("User is inactive.")
        except InvalidCredentialsException as exc:
            logger.warning(exc.message)
            await self.__revoke_user_tokens(decoded_refresh_token.user_id)
            raise InvalidCredentialsException from None
        except InactiveUserException as exc:
            logger.warning(exc.message)
            await self.__revoke_user_tokens(decoded_refresh_token.user_id)
            raise
        except SecretLeakException as exc:
            # This check is silly. If attackers get the secret, they shouldn't make this silly mistake.
            logger.error(exc.message)
            # revoke tokens for both users
            for user_id in exc.user_ids:
                await self.__revoke_user_tokens(user_id)
            raise InvalidCredentialsException from None

        return decoded_refresh_token
