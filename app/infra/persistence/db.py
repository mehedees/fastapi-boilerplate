from collections.abc import Callable, Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.core.settings import Settings
from app.infra.persistence.models.base import BaseDBModel


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = self.__create_engine()
        self.__session_factory: Callable[[], Session] = scoped_session(
            sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        )
        self.initialize_db_tables()

    def __create_engine(self) -> Engine:
        return create_engine(
            self.settings.database_url,
            echo=self.settings.DEBUG,
            pool_size=self.settings.DATABASE_POOL_SIZE,
            max_overflow=10,
            pool_recycle=self.settings.DATABASE_POOL_RECYCLE,
            pool_timeout=self.settings.DATABASE_POOL_TIMEOUT,
            pool_pre_ping=True,
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False,
            },
        )

    @contextmanager
    def session_factory(
        self, auto_commit: bool = True, read_only: bool = False
    ) -> Generator[Session]:
        """
        Provide a transactional scope around a series of operations.
        Usage:

            with db.session_factory(auto_commit=True, read_only=False) as session:
                # use session here
                pass

        Args:
            auto_commit (bool): If True, commit the transaction if no exceptions occur.
            read_only (bool): If True, do not commit or rollback the transaction.
        Yields:
            Session: SQLAlchemy session object.
        """
        session = self.__session_factory()
        try:
            yield session
            if auto_commit and not read_only:
                session.commit()
        except Exception:
            if not read_only:
                session.rollback()
            raise
        finally:
            session.close()

    def initialize_db_tables(self):
        BaseDBModel.metadata.create_all(bind=self.engine)

    def __del__(self):
        self.engine.dispose()
