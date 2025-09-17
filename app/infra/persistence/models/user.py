from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseDBModel


class UserModel(BaseDBModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )
