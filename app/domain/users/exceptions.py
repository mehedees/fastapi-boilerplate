from app.core.exceptions import CustomException


class UserAlreadyExist(CustomException):
    pass


class UserNotFoundException(CustomException):
    pass


class InvalidPasswordException(CustomException):
    pass


class InvalidCredentialsException(CustomException):
    pass
