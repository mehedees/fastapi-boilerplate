from sqlmodel import Session

from app.core.utils.auth import SecureHashManager
from app.domain.users.entities import User
from app.core.settings import get_settings


settings = get_settings()

class UserService:
    def __init__(self, session: Session):
        self.session = session

    # Add user-related business logic methods here
    async def get_user_by_email(self, email: str) -> User:
        ...

    async def create_user(self, user: User) -> User:
        hashed_password = SecureHashManager(
            settings.SECRET_KEY
        ).hash_password_argon2(user.password)
