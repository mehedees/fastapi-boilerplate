from dependency_injector import containers, providers

from app import scripts
from app.api import v1 as api_v1
from app.core.settings import Settings
from app.core.utils.auth import SecureHashManager
from app.core.utils.token import TokenUtils
from app.core.utils.user_agent import UserAgentUtil
from app.domain.users.services import UserService
from app.infra.persistence.db import Database
from app.infra.persistence.repo_impl.refresh_token_repo_impl import RefreshTokenRepoImpl
from app.infra.persistence.repo_impl.user_repo_impl import UserRepoImpl


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    config = providers.Configuration()

    settings = providers.Singleton(Settings)

    # Infrastructure - Database
    database = providers.Resource(Database, settings=settings)

    # hash manager
    hash_manager = providers.Singleton(
        SecureHashManager, secret_key=settings.provided.SECRET_KEY
    )

    # token util
    token_util = providers.Singleton(
        TokenUtils,
        access_token_secret_key=settings.provided.ACCESS_TOKEN_SECRET_KEY,
        refresh_token_secret_key=settings.provided.REFRESH_TOKEN_SECRET_KEY,
        algorithm=settings.provided.AUTH_TOKEN_ALGORITHM,
    )

    user_agent_util = providers.Singleton(
        UserAgentUtil,
    )

    # Repositories
    user_repository = providers.Factory(
        UserRepoImpl,
        session_factory=database.provided.session_factory,
    )

    refresh_token_repository = providers.Factory(
        RefreshTokenRepoImpl,
        session_factory=database.provided.session_factory,
    )

    # Domain Services
    user_service = providers.Factory(
        UserService,
        settings=settings,
        repo=user_repository,
        refresh_token_repo=refresh_token_repository,
        hash_manager=hash_manager,
        token_util=token_util,
        user_agent_util=user_agent_util,
    )


def setup_container(settings: Settings) -> Container:
    """
    Setup and configure the DI container.
    Call this during application startup.
    """
    container = Container()
    container.config.from_pydantic(settings)

    # Wire modules for automatic injection
    container.wire(packages=[api_v1, scripts])

    return container


# # Dependency injection helpers for FastAPI
# def get_user_service():
#     """FastAPI dependency for UserService."""
#     return Provide[Container.user_service]


# def get_payment_service():
#     """FastAPI dependency for PaymentService."""
#     return Provide[Container.payment_service]


# def get_user_repository():
#     """FastAPI dependency for UserRepository."""
#     return Provide[Container.user_repository]


# def get_payment_repository():
#     """FastAPI dependency for PaymentRepository."""
#     return Provide[Container.payment_repository]


# # Example of how to use in FastAPI views:
# """
# # In api/v1/users/views.py

# from fastapi import Depends
# from dependency_injector.wiring import inject, Provide
# from core.container import Container
# from domain.users.services import UserService

# class UserController:
#     @inject
#     def __init__(
#         self,
#         user_service: UserService = Depends(Provide[Container.user_service])
#     ):
#         self.user_service = user_service

# # Or using the helper functions:
# from core.container import get_user_service

# @router.post("/users")
# async def create_user(
#     user_service: UserService = Depends(get_user_service),
# ):
#     # Use user_service
#     pass
# """
