from enum import Enum


class EnvironmentEnum(str, Enum):
    DEV = "development"
    PROD = "production"
