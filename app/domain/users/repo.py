from typing import Protocol

from sqlalchemy.orm import Session

from app.domain.users.entities import UserCreateEntity, UserEntity


class UserRepo(Protocol):
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: UserCreateEntity) -> UserEntity: ...
