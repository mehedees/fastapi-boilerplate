from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


class BaseDBModel(DeclarativeBase):
    def to_dataclass(self, dataclass_cls):
        field_names = {f.name for f in dataclass_cls.__dataclass_fields__.values()}
        data = {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
            if c.key in field_names
        }
        return dataclass_cls(**data)
