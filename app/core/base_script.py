from app.core.container import Container, setup_container
from app.core.settings import get_settings


class BaseScript:
    def __init__(self):
        print("Initializing Base Script")
        self.conainer: Container | None = None

    def __enter__(self):
        print("Entering Base Script")
        settings = get_settings()
        container = setup_container(settings)
        container.init_resources()
        self.container = container
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting Base Script")
        self.container.shutdown_resources()
