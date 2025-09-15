import asyncio

from dependency_injector.wiring import inject
from pydantic import SecretStr

from app.api.v1.users.schema import UserCreateSchema
from app.core.base_script import BaseScript
from app.domain.users.entities import UserCreateEntity, UserEntity
from app.domain.users.services import UserService


class CreateFirstUser(BaseScript):
    @inject
    async def create_first_user(
        self,
        # user_service: UserService = Provide[Container.user_service]
    ):
        user_service: UserService = self.container.user_service
        # Check if there is a user in the database
        first_user: tuple[UserEntity] = await user_service.list_users(limit=1)
        if first_user:
            print("First user exists already")
            return

        # take user ifo input
        email = input("Email: ")
        name = input("Name: ")
        password = SecretStr(input("Password: "))
        confirm_password = SecretStr(input("Confirm Password: "))

        try:
            user_create_schema = UserCreateSchema(
                email=email,
                name=name,
                password=password,
                confirm_password=confirm_password,
            )
        except ValueError as e:
            print(e)
            return

        try:
            created_user = await user_service.create_user(
                UserCreateEntity(**user_create_schema.model_dump())
            )
            print(f"Created user {created_user.name}")
        except Exception as e:
            print(e)
            return


if __name__ == "__main__":
    with CreateFirstUser() as script:
        try:
            print("Creating first user...")
            asyncio.run(script.create_first_user())
        except Exception as e:
            print(e)
