from .api import APIException


class CustomException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message


__all__ = ["APIException", "CustomException"]
