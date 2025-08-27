from functools import lru_cache

from sqlmodel import create_engine

from app.core.settings import get_settings

settings = get_settings()


@lru_cache
def get_engine():
    return create_engine(
        settings.database_url,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=10,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_pre_ping=True,
    )
