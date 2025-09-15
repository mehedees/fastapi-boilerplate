import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, SecretStr, ValidationInfo

from app.domain.users.constants import PASSWORD_REGEX


def validate_passwords(value: SecretStr) -> SecretStr:
    secret_value: str = value.get_secret_value()
    if not re.compile(PASSWORD_REGEX).match(secret_value):
        raise ValueError(
            "Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character and minimum 8 characters"
        )
    return value


def check_passwords_match(value: SecretStr, info: ValidationInfo) -> SecretStr:
    if info.field_name == "confirm_password":
        if value.get_secret_value() != info.data.get("password").get_secret_value():
            raise ValueError("Passwords do not match")
    return value


class UserCreateSchema(BaseModel):
    email: str
    name: str
    password: Annotated[SecretStr, AfterValidator(validate_passwords)]
    confirm_password: Annotated[SecretStr, AfterValidator(check_passwords_match)]
