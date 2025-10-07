from .api import APIException


class CustomException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message


class NotFoundException(CustomException):
    pass


__all__ = ["APIException", "CustomException", "NotFoundException"]
