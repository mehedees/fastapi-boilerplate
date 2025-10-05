import asyncio

from dependency_injector.wiring import Provide, inject
from pydantic import SecretStr

from app.api.v1.users.schema import UserCreateRequest
from app.core.container import Container, setup_container
from app.core.settings import get_settings
from app.domain.users.entities.user_entities import UserCreateEntity, UserEntity
from app.domain.users.services import UserService
from app.scripts.base import BaseScript


class CreateFirstUser(BaseScript):
    async def create_first_user(self, user_service: UserService):
        # Check if there is a user in the database
        print("in...")
        first_user: tuple[UserEntity, ...] = await user_service.list_users(limit=1)
        if first_user:
            print("First user exists already")
            return

        # take user ifo input
        email = input("Email: ")
        name = input("Name: ")
        password = SecretStr(input("Password: "))
        confirm_password = SecretStr(input("Confirm Password: "))

        try:
            user_create_schema = UserCreateRequest(
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
                UserCreateEntity(
                    email=user_create_schema.email,
                    name=user_create_schema.name,
                    password=user_create_schema.password.get_secret_value(),
                )
            )
            print(f"Created user {created_user.name}")
        except Exception as e:
            print(e)
            return


@inject
async def main(user_service: UserService = Provide[Container.user_service]):
    with CreateFirstUser() as script:
        try:
            print("Creating first user...")
            await script.create_first_user(user_service)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    settings = get_settings()
    container: Container = setup_container(settings)
    container.wire(modules=[__name__])
    container.init_resources()
    asyncio.run(main())
    print("Shutting down...")
    container.shutdown_resources()
