from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.db import BaseDBModel


class User(BaseDBModel):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String(100), unique=True, nullable=False)
    name: str = Column(String(100), nullable=False)
    password: str = Column(String(100), nullable=False)

    created_at: datetime | None = Column(DateTime, server_default=func.now())
    updated_at: datetime | None = Column(DateTime, server_default=func.now())
