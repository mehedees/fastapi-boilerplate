from app.core.settings import get_settings
from app.core.utils.auth import SecureHashManager
from app.domain.users.entities import UserCreateEntity, UserEntity
from app.domain.users.repo import UserRepo

settings = get_settings()


class UserService:
    def create_user(self, user: UserCreateEntity, repo: UserRepo) -> UserEntity:
        user.password = SecureHashManager(settings.SECRET_KEY).hash_password_argon2(
            user.password
        )

        print("hashed password", user.password)

        new_user: UserEntity = repo.create_user(user)

        return new_user
