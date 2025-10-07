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
    HEALTHCHECK_ENDPOINT: str = "/health"

    # Secret Key
    SECRET_KEY: str
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    REFRESH_TOKEN_EXPIRE_SECONDS: int
    AUTH_TOKEN_ALGORITHM: str = "HS256"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    AUTH_LOGIN_PATH: str = f"{API_V1_PREFIX}/users/login"
    AUTH_TOKEN_REFRESH_PATH: str = f"{API_V1_PREFIX}/users/refresh-token"
    AUTH_LOGOUT_PATH: str = f"{API_V1_PREFIX}/users/logout"
    AUTH_EXCLUDE_PATHS: list[str] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        HEALTHCHECK_ENDPOINT,
        AUTH_LOGIN_PATH,
        AUTH_TOKEN_REFRESH_PATH,
        AUTH_LOGOUT_PATH,
    ]

    # Database
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_POOL_RECYCLE: int = 14400
    DATABASE_POOL_TIMEOUT: int = 30

    @property
    def database_url(self):
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:3306/{self.DATABASE_NAME}"
        )

    # CORS
    ALLOWED_ORIGINS: list[str]
    ALLOWED_METHODS: list[str]
    ALLOWED_HEADERS: list[str]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
