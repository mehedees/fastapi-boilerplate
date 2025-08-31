from app.core.db import initialize_db, shutdown_db
from app.core.settings import get_settings

settings = get_settings()


class BaseScript:
    def __init__(self):
        print("Initializing Base Script")

    def __enter__(self):
        print("Entering Base Script")
        initialize_db(settings)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting Base Script")
        shutdown_db()
