from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    username: str = Field(primary_key=True, unique=True)
    email: str = Field(unique=True)
    first_name: str
    last_name: str
    middle_name: str | None = None
    password: str
