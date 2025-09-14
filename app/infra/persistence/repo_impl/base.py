from collections.abc import Callable

from sqlalchemy.orm import Session

from app.infra.persistence.models.base import DBModel


class BaseRepoImpl:
    def __init__(self, model: type[DBModel], session_factory: Callable[..., Session]):
        self.__model = model
        self.session = session_factory()
