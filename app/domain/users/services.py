from app.core.settings import get_settings
from app.core.utils.auth import SecureHashManager
from app.domain.users.entities import UserCreateEntity, UserEntity
from app.domain.users.repo import UserRepo

settings = get_settings()


class UserService:
    def __init__(self, repo: UserRepo, hash_manager: SecureHashManager) -> None:
        self.repo = repo
        self.hash_manager = hash_manager

    def create_user(self, user: UserCreateEntity) -> UserEntity:
        user.password = self.hash_manager.hash_password_argon2(user.password)

        print("hashed password", user.password)

        new_user: UserEntity = self.repo.create_user(user)

        return new_user
