import dataclasses
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.infra.persistence.models.base import DBModel


class BaseRepoImpl:
    def __init__(self, model: type[DBModel], session_factory: Callable[..., Session]):
        self.__model = model
        self.session = session_factory()

    async def create(self, data: dict, entity_type: type[dataclasses]) -> object:
        obj = self.__model(**data)
        self.session.add(obj)
        self.session.flush()
        print("after flush: ", obj)
        self.session.refresh(obj)
        print("after refresh: ", obj)

        return obj.to_dataclass(entity_type)

    async def get(self, query: dict) -> object:
        pass
