from sqlmodel import Session

from app.domain.users.entities import User


class UserService:
    def __init__(self, session: Session):
        self.session = session

    # Add user-related business logic methods here
    async def get_user_by_email(self, email: str) -> User:
        ...
