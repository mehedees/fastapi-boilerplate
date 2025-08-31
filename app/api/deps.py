from app.core.db.client import get_session


# Dependency for FastAPI
def get_db():
    session = get_session()
    try:
        yield session
    finally:
        session.close()
