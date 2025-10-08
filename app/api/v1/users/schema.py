import re
from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    SecretStr,
    ValidationInfo,
)
from pydantic_settings import SettingsConfigDict

from app.domain.users.constants import PASSWORD_REGEX


def validate_password(value: SecretStr) -> SecretStr:
    """
    Validates that the password meets the required complexity:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Minimum length of 8 characters

    Args:
        value (SecretStr): The password to validate.
    Returns:
        SecretStr: The validated password.
    Raises:
        ValueError: If the password does not meet the complexity requirements.
    """
    secret_value: str = value.get_secret_value()
    if not re.compile(PASSWORD_REGEX).match(secret_value):
        raise ValueError(
            "Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character and minimum 8 characters"
        )
    return value


def check_passwords_match(value: SecretStr, info: ValidationInfo) -> SecretStr:
    """
    Validates that the password and confirm_password fields match.

    Args:
        value (SecretStr): The confirm_password value to validate.
        info (ValidationInfo): Additional validation context.
    Returns:
        SecretStr: The validated confirm_password.
    Raises:
        ValueError: If the passwords do not match or if the password is not set.
    """
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


class LoginToken(BaseModel):
    access_token: str
    access_token_iat: datetime
    access_token_exp_seconds: int
    refresh_token_iat: datetime
    refresh_token_exp_seconds: int
    token_type: str

    model_config = SettingsConfigDict(extra="ignore")


class UserProfile(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
