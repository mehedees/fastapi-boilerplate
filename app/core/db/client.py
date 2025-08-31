from sqlmodel import Session, SQLModel

from .engine import get_engine


def get_session():
    """
    Create a new SQLModel session.
    MUST CLOSE the session after use.
    :return: SQLModel Session
    """
    engine = get_engine()
    return Session(engine)


# For migrations or app startup
def init_db():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
