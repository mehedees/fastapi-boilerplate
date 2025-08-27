from sqlmodel import Session, SQLModel

from .engine import get_engine


# Dependency for FastAPI
def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


# For migrations or app startup
def init_db():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
