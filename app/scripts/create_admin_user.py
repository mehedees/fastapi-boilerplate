from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlmodel import select

from app.core.base_script import BaseScript
from app.domain.users.models import User


class CreateFirstUser(BaseScript):
    def create_first_user(self):
        try:
            self.session.exec(select(User)).one()
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

        user = User(
            email=email,
            name=name,
            password=password,
        )

        self.session.add(user)
        self.session.commit()
        print(f"Created user {user.name} successfully")
        return


if __name__ == "__main__":
    with CreateFirstUser() as script:
        try:
            script.create_first_user()
        except Exception as e:
            print(e)
