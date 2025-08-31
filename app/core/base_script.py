from app.core.db import get_engine, get_session


class BaseScript:
    def __init__(self):
        print("Initializing Base Script")
        self.session = None
        self.engine = None

    def __enter__(self):
        print("Entering Base Script")
        self.engine = get_engine()
        self.session = get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting Base Script")
        self.session.close()
        self.engine.dispose()
        self.session = None
        self.engine = None
