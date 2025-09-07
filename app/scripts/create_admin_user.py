from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from app.core.base_script import BaseScript
from app.core.db import managed_db_context
from app.domain.users.entities import UserCreateEntity, UserEntity
from app.domain.users.services import UserService
from app.infra.persistence.models.user import UserModel
from app.infra.persistence.repo_impl.user import UserRepoImpl


class CreateFirstUser(BaseScript):
    @staticmethod
    def create_first_user():
        with managed_db_context() as db:
            try:
                db.query(UserModel).one()
                print("First user exists already")
                return
            except MultipleResultsFound:
                print("Multiple users found")
                return
            except NoResultFound:
                print("No user found, proceeding to user create")

            email: str = input("Email: ")
            name: str = input("Name: ")
            password: str = input("Password: ")

            if not email or not name or not password:
                raise ValueError("Email, name and password are required")

            user_entity = UserCreateEntity(email=email, name=name, password=password)

            user: UserEntity = UserService().create_user(
                user_entity, UserRepoImpl(session=db)
            )

            print(f"Created user {user.name}")
            return


if __name__ == "__main__":
    with CreateFirstUser() as script:
        try:
            script.create_first_user()
        except Exception as e:
            print(e)
