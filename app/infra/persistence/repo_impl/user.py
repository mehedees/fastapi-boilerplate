from dataclasses import asdict

from sqlalchemy.orm import Session

from app.domain.users.entities import UserCreateEntity, UserEntity
from app.infra.persistence.models.user import UserModel


class UserRepoImpl:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: UserCreateEntity) -> UserEntity:
        obj = UserModel(**asdict(user))
        print(obj)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        print(obj)

        return obj.to_dataclass(UserEntity)
