from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.db.utils import initialize_db_tables
from app.core.settings import Settings

engine: Engine | None = None
DBSession: sessionmaker | None = None
BaseDBModel = declarative_base()


def _get_engine(settings: Settings) -> Engine:
    """
    Create a SQLAlchemy engine from the settings object.
    :param settings:
    :return: sqlalchemy.engine.Engine
    """
    return create_engine(
        settings.database_url,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=10,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_pre_ping=True,
        connect_args={
            "charset": "utf8mb4",
            "autocommit": False,
        },
    )


def initialize_db(settings: Settings) -> None:
    """
    Initialize the database and create the engine and session maker.
    :param settings:
    :return:
    """
    global engine, DBSession
    engine = _get_engine(settings)
    DBSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    initialize_db_tables(engine, BaseDBModel)


def shutdown_db() -> None:
    """
    Shutdown the engine and sessionmaker.
    :return:
    """
    global engine, DBSession
    if engine is not None:
        engine.dispose()
        engine = None
        DBSession = None


def get_db() -> Generator:
    """
    Dependency for FastAPI.
    Does not handle commit. Performs rollback on exception and reraises.
    Closes session finally.
    :return: DBSession generator
    """
    global DBSession
    if DBSession is None:
        raise RuntimeError("DBSession not initialized")

    db = DBSession()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def managed_db_context():
    """
    Context manager that creates a new DB session and closes it.
    Performs commit on success case, else rollback on exception.
    Closes session finally.
    :return:
    """
    global DBSession
    if DBSession is None:
        raise RuntimeError("DBSession not initialized")

    db = DBSession()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
