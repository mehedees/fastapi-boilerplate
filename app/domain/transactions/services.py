"""
Transaction service for managing complex multi-operation database transactions.

This service provides utilities for handling scenarios where multiple interdependent
operations need to be performed within a single database transaction.
"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import TypeVar

from sqlalchemy.orm import Session

from app.infra.persistence.db import Database

T = TypeVar("T")


class TransactionService:
    """
    Service for managing complex database transactions.

    This service provides utilities for handling scenarios where multiple
    interdependent operations need to be performed within a single transaction.
    """

    def __init__(self, database: Database):
        self.database = database

    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """
        Provide a manual transaction context for complex multi-operation scenarios.

        This is the primary method for handling multiple interdependent operations
        within a single transaction. All operations will be committed together
        or rolled back on any exception.

        Usage:
            async with transaction_service.transaction() as session:
                # Perform multiple operations
                user = UserModel(...)
                session.add(user)
                session.flush()  # Get the ID

                token = RefreshTokenModel(user_id=user.id, ...)
                session.add(token)

                # All operations will be committed together
                # or rolled back if any exception occurs

        Yields:
            Session: SQLAlchemy session object with manual transaction control.
        """
        with self.database.transaction() as session:
            yield session

    async def execute_in_transaction(
        self, operation: Callable[[Session], T]
    ) -> T:
        """
        Execute a function within a transaction context.

        This is useful when you have a function that needs to perform multiple
        operations and you want to ensure they all succeed or fail together.

        Args:
            operation: A callable that takes a Session and returns a result

        Returns:
            The result of the operation

        Raises:
            Any exception raised by the operation will cause a rollback
        """
        with self.database.transaction() as session:
            return operation(session)

    @contextmanager
    def read_only_transaction(self) -> Generator[Session, None, None]:
        """
        Provide a read-only transaction context.

        This is useful for complex read operations that need to maintain
        consistency across multiple queries.

        Usage:
            async with transaction_service.read_only_transaction() as session:
                # Perform multiple read operations
                users = session.query(UserModel).all()
                tokens = session.query(RefreshTokenModel).all()
                # All reads will see a consistent snapshot

        Yields:
            Session: SQLAlchemy session object for read-only operations.
        """
        with self.database.session_factory(read_only=True) as session:
            yield session

    def get_session_factory(self) -> Callable[[], Session]:
        """
        Get the session factory for dependency injection.

        This is useful when you need to pass the session factory to other
        services or repositories that need to work within a transaction.

        Returns:
            Callable that creates a new session
        """
        return self.database.session_factory
