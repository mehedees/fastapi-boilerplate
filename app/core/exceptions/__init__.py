from .api import APIException


class CustomException(Exception):
    """
    Base class for custom exceptions in the application.
    """
    def __init__(self, message: str | None = None):
        self.message = message


class NotFoundException(CustomException):
    pass


__all__ = ["APIException", "CustomException", "NotFoundException"]
