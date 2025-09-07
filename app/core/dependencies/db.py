from collections.abc import Generator

from sqlalchemy.orm import Session

from app.infra.persistence.db import db as database

# Convenience type alias for dependency injection
DbSession = Session


class DatabaseDependency:
    """Database session dependency for FastAPI dependency injection and context management.

    This class provides a flexible way to manage database sessions in FastAPI applications,
    supporting both dependency injection and context manager patterns. It handles session
    lifecycle, automatic commits, and rollbacks based on configuration.

    Args:
        auto_commit (bool): If True, automatically commits changes at the end of session.
            Defaults to True.
        read_only (bool): If True, disables commit operations. Defaults to False.

    Usage as dependency:
        @app.get("/items")
        def get_items(db: Session = Depends(DatabaseDependency())):
            return db.query(Item).all()
    Or with custom configuration:
        @app.get("/items")
        def get_items(db: Session = Depends(DatabaseDependency(auto_commit=False, read_only=True))):
            return db.query(Item).all()
    Or with pre-configured dependency instances:
        @app.get("/items")
        def get_items(db: Session = Depends(get_auto_commit_db)):
            return db.query(Item).all()

    Usage as context manager:
        with DatabaseDependency() as session:
            session.query(Item).all()
    """

    def __init__(self, auto_commit: bool = True, read_only: bool = False):
        self.auto_commit = auto_commit
        self.read_only = read_only
        self.session = None

    def __call__(self) -> Generator[Session, None]:
        session = database.get_session()
        try:
            yield session
            if self.auto_commit and not self.read_only:
                session.commit()
        except Exception:
            if not self.read_only:
                session.rollback()
            raise
        finally:
            session.close()

    def __enter__(self) -> Session:
        self.session = database.get_session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if not self.read_only:
                self.session.rollback()
            self.session.close()
            raise exc_type(exc_val).with_traceback(exc_tb)
        if self.auto_commit and not self.read_only:
            self.session.commit()
        self.session.close()


# Pre-configured dependency instances
get_read_only_db = DatabaseDependency(auto_commit=False, read_only=True)
get_manual_commit_db = DatabaseDependency(auto_commit=False, read_only=False)
get_auto_commit_db = DatabaseDependency(auto_commit=True, read_only=False)
