from warnings import warn

from app.core.exceptions import CustomException


class UserAlreadyExist(CustomException):
    pass


class InactiveUserException(CustomException):
    pass


class UserNotFoundException(CustomException):
    """This exception is deprecated and will be removed in future versions.

    Please handle specific cases with generic app.core.exceptions.NotFoundException or use custom error handling.
    """

    def __init__(self, *args, **kwargs):
        warn(
            "UserNotFoundException is deprecated and will be removed in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class InvalidPasswordException(CustomException):
    pass


class InvalidCredentialsException(CustomException):
    pass


class SecretLeakException(CustomException):
    def __init__(self, user_ids: list[int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_ids = user_ids
