from app.core.utils.auth import SecureHashManager
from app.domain.users.entities import LoginRequestEntity, UserCreateEntity, UserEntity
from app.domain.users.exceptions import (
    InvalidPasswordException,
    UserAlreadyExist,
    UserNotFoundException,
)
from app.domain.users.repo import UserRepo


class UserService:
    def __init__(self, repo: UserRepo, hash_manager: SecureHashManager) -> None:
        self.__repo = repo
        self.__hash_manager = hash_manager

    async def create_user(self, user: UserCreateEntity) -> UserEntity:
        # check if user already exists
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

    async def login(self, login_req_payload: LoginRequestEntity):
        # fetch user if exists
        user: UserEntity | None = await self.__repo.get_user_by_email(
            login_req_payload.email
        )
        if user is None:
            raise UserNotFoundException

        # match password
        if not self.__hash_manager.verify_password_argon2(
            login_req_payload.password, user.password
        ):
            raise InvalidPasswordException
