from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import Settings


class DB:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = self.__create_engine()
        self.session_factory = self.__get_session_maker()

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

    def __get_session_maker(self):
        return sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_session(self):
        with self.session_factory() as session:
            yield session

    def __del__(self):
        self.engine.dispose()


db: DB | None = None


def start_db(settings: Settings):
    global db
    db = DB(settings)
