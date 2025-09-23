import re
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    EmailStr,
    SecretStr,
    ValidationInfo,
)

from app.domain.users.constants import PASSWORD_REGEX


def validate_password(value: SecretStr) -> SecretStr:
    secret_value: str = value.get_secret_value()
    if not re.compile(PASSWORD_REGEX).match(secret_value):
        raise ValueError(
            "Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character and minimum 8 characters"
        )
    return value


def check_passwords_match(value: SecretStr, info: ValidationInfo) -> SecretStr:
    password: SecretStr | None = info.data.get("password")
    if password is None:
        raise ValueError("Password must be set")
    if info.field_name == "confirm_password":
        if value.get_secret_value() != password.get_secret_value():
            raise ValueError("Passwords do not match")
    return value


class UserCreateRequest(BaseModel):
    email: str  # TODO EmailStr
    name: str
    password: Annotated[SecretStr, BeforeValidator(validate_password)]
    confirm_password: Annotated[SecretStr, AfterValidator(check_passwords_match)]


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr
