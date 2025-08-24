from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums import EnvironmentEnum


class Settings(BaseSettings):
    # Application
    APP_NAME: str
    APP_VERSION: str
    ENVIRONMENT: EnvironmentEnum
    DEBUG: bool
    LOG_LEVEL: str
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_URL: str = ""


    # CORS
    ALLOWED_ORIGINS: list[str]
    ALLOWED_METHODS: list[str]
    ALLOWED_HEADERS: list[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
