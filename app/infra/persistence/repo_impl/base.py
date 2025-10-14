from collections.abc import Callable

from sqlalchemy.orm import Session

from app.infra.persistence.models.base import DBModel


class BaseRepoImpl:
    def __init__(
        self,
        model: type[DBModel],
        session_factory: Callable[..., Session],
    ):
        self.__model = model
        self.session_factory = session_factory

    def _get_session(self, session: Session | None = None) -> Session:
        """
        Get a session for database operations.

        Args:
            session: Optional existing session. If provided, use it instead of creating a new one.

        Returns:
            Session: SQLAlchemy session object.
        """
        if session is not None:
            return session
        return self.session_factory()
