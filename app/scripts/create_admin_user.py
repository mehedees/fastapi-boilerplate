from dataclasses import asdict

from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from app.core.base_script import BaseScript
from app.core.db import managed_db_context
from app.domain.users.entities import UserCreate
from app.domain.users.models import User


class CreateFirstUser(BaseScript):
    @staticmethod
    def create_first_user():
        with managed_db_context() as db:
            try:
                db.query(User).one()
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

            user_entity = UserCreate(email=email, name=name, password=password)

            user = User(**asdict(user_entity))

            print(f"Creating user {user.name}")
            db.add(user)
            return


if __name__ == "__main__":
    with CreateFirstUser() as script:
        try:
            script.create_first_user()
        except Exception as e:
            print(e)
